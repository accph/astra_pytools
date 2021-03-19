import numpy as np
from glob import glob
from astratools import make_file, run_ASTRA, remove_files
from astraproc import _process2, get_d, getP, rotate

def get_M(lattice, bunch, r0=(0,0), phi0=0, rel_devs=[1e-3]*6):
    M = np.zeros((6,6))

    temp_name = f'{lattice}_astra_M'
    temp_bunch_name = f'{temp_name}_bunch.ini'
    for k in range(6):
        remove_files(temp_name)
        remove_files(temp_bunch_name)

        x0_var = _generate_beam(temp_bunch_name, bunch, \
                                r0, phi0, k, rel_devs[k])
        make_file(lattice, temp_name, { 'Distribution' : temp_bunch_name,
                                        'Zphase' : 1,
                                        'RUN' : 1,
                                        'LEField' : 'F'})
        run_ASTRA(temp_name)

        files = glob(f'{temp_name}.[0-9]*.001')
        if len(files) == 0:
            return None

        beam, _ = _process2(files[0], status_flags=[3], ref_particle=0)

        M[0,k] = np.polyfit(x0_var, beam[:,0], 1)[0]
        M[1,k] = np.polyfit(x0_var, beam[:,6], 1)[0]
        M[2,k] = np.polyfit(x0_var, beam[:,1], 1)[0]
        M[3,k] = np.polyfit(x0_var, beam[:,7], 1)[0]
        M[4,k] = np.polyfit(x0_var, -1.*beam[:,2], 1)[0]
        M[5,k] = np.polyfit(x0_var, get_d(beam), 1)[0]

        remove_files(temp_name)
        remove_files(temp_bunch_name)

    return M

def _generate_beam(temp_bunch_name, bunch, r0, phi0, k, rel_dev):
    N = 10
    beam, data = _process2(bunch)

    s0 = np.std(data[1:,:3], axis=0)
    p0 = np.mean(getP(beam))

    new_data = np.zeros((N, 10))
    new_data[:,[5,7,8,9]] = [p0, 1.6e-10, 1, 3]

    var = rel_dev*np.linspace(0., 1., N)
    res = None
    if k == 0:
        res = new_data[:,0] = s0[0]*var
    elif k == 2:
        res = new_data[:,1] = s0[1]*var
    elif k == 1:
        res = var
        new_data[:,[3,5]] = p0*np.column_stack((np.sin(var), np.cos(var)))
    elif k == 3:
        res = var
        new_data[:,[4,5]] = p0*np.column_stack((np.sin(var), np.cos(var)))
    elif k == 4:
        res = -1.*s0[2]*var
        new_data[:,2] = s0[2]*var
    elif k == 5:
        res = var
        new_data[:,5] += p0*var

    new_data[1:,[2,5,6]] -= new_data[0,[2,5,6]]
    new_data = rotate(new_data, phi=phi0, ref_particle=0)
    new_data[:,0] += r0[0]
    new_data[0,2] += r0[1]

    # add ballast particles
    cond = np.logical_or.reduce([data[:,9]==flag for flag in (-1,-3,5)])
    data = data[cond, :]
    new_data = np.append(new_data, data[1:10, :], axis=0)

    np.savetxt(temp_bunch_name, new_data, fmt='% .6e '*8 + '% i '*2)
    return res

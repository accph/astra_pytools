import numpy as np

def process(filename, return_data=False, monitor=False, phi=None):
    """
    Process ASTRA output data. Return the beam end parameters
    -------
    args:
        filename : str
            The name of ASTRA input file.
    -------
    return : dict
        key - name of the beam parameter,
        value - its value.

        keys: [ 'sig_X', 'sig_Y', 
                'norm_emit_X', 'norm_emit_Y',
                'beta_X', 'beta_Y',
                'disp', 'disp_a' ]
    """
    try:
        data = np.loadtxt(filename, dtype = 'float64')
    except OSError:
        return (None, None, None) if return_data else None
    else:
        cond = np.logical_or(data[:,9]==5, data[:,9]==3)
        cond = np.logical_or(cond, data[:,9]==-3)
        cond = np.logical_or(cond, data[:,9]==-1)
        data = data[cond,:]
        beam = inNewCoordSys(data, phi=None)
        endParam = getEndParam(beam, monitor)
        return (endParam, beam, data) if return_data else endParam

def _process2(filename, phi=None, status_flags=[3,5], ref_particle=None):
    try:
        data = np.loadtxt(filename, dtype = 'float64')
    except OSError:
        return (None, None)
    else:
        cond = np.logical_or.reduce([data[:,9]==flag for flag in status_flags])
        data = data[cond, :]

        beam = inNewCoordSys(data, phi, ref_particle)
        return (beam, data)

def rotate(_data, phi=None, ro=None, ref_particle=None):
    data = np.copy(_data)
    data[1::, 2] = data[1::, 2] + data[0, 2]
    data[1::, 5] = data[1::, 5] + data[0, 5]

    if ro is None:
        if ref_particle is None:
            data[:, [0,2]] -= np.mean(data[:, [0,2]], axis=0)
        else:
            data[:, [0,2]] -= data[ref_particle, [0,2]]
    else:
        data[:, [0,2]] -= ro

    if phi is None:
        if ref_particle is None:
            Px0, Pz0 = np.mean(data[:, [3,5]], axis=0)
            phi = np.arctan(Px0/Pz0)
        else:
            phi = np.arctan(data[ref_particle,3]/data[ref_particle,5])

    X  = data[:, 0] * np.cos(phi) - data[:, 2] * np.sin(phi)
    Z  = data[:, 0] * np.sin(phi) + data[:, 2] * np.cos(phi)
    Px = data[:, 3] * np.cos(phi) - data[:, 5] * np.sin(phi)
    Pz = data[:, 3] * np.sin(phi) + data[:, 5] * np.cos(phi)
    Y  = data[:, 1]
    Py = data[:, 4]

    Z[1:] -= Z[0]
    Pz[1:] -= Pz[0]

    data[:,0:6] = np.column_stack((X, Y, Z, Px, Py, Pz))
    return data


def inNewCoordSys(_data, phi=None, ref_particle=None):
    """
    Return : numpy array
        Data in the following table: [X, Y, Z, Px, Py, Pz, X', Y', T]
    """
    data = rotate(_data, phi, ref_particle)
    
    data[1:,[2,5,6]] += data[0,[2,5,6]]

    AngleX = data[:,3] / data[:,5]
    AngleY = data[:,4] / data[:,5]

    return np.column_stack((data[:,0:6], AngleX, AngleY, data[:,6]))

def getEndParam(beam, monitor=False):
    endParam = {}

    X = beam[:,0] - np.mean(beam[:,0])
    Y = beam[:,1] - np.mean(beam[:,1])
    aX = beam[:,6]
    aY = beam[:,7]
    #aX = beam[:,6] - np.mean(beam[:,6])
    #aY = beam[:,7] - np.mean(beam[:,7])
    Z = beam[:,2]

    if monitor:
        beam[:,0] = X - aX*Z
        beam[:,1] = Y - aY*Z

    endParam['sig_X'] = np.std(beam[:,0])
    endParam['sig_Y'] = np.std(beam[:,1])
    endParam['norm_emit_X'] = getNormEmittance(beam, 0)
    endParam['norm_emit_Y'] = getNormEmittance(beam, 1)



    endParam['beta_X'] = np.mean(X**2)/getEmittance(beam, 0)
    endParam['beta_Y'] = np.mean(Y**2)/getEmittance(beam, 1)
    endParam['alpha_X'] = -np.mean(X*aX)/getEmittance(beam, 0)
    endParam['alpha_Y'] = -np.mean(Y*aY)/getEmittance(beam, 1)

    endParam['disp'] = np.polyfit(get_d(beam), beam[:,0], 3)[::-1]
    endParam['disp_a'] = np.polyfit(get_d(beam), beam[:,6], 3)[::-1]

    return endParam

def getEmittance(beam, axis):
    X = beam[:, 0 + axis] - np.mean(beam[:, 0 + axis])
    AngleX = beam[:, 6 + axis] - np.mean(beam[:, 6 + axis])
    #Z = beam[:, 2] - np.mean(beam[:, 2])

    #X = X - AngleX * Z
    return np.sqrt(np.mean(X**2)*np.mean(AngleX**2) - np.mean(X*AngleX)**2)

def getP(beam):
    Px = beam[:,3]
    Py = beam[:,4]
    Pz = beam[:,5]
    return np.sqrt(Px**2 + Py**2 + Pz**2)

def get_d(beam):
    P = getP(beam)
    return P/np.mean(P) - 1

def getE(beam):
    m = 0.511*10**6
    return np.sqrt(getP(beam)**2 + m**2)

def getNormEmittance(beam, axis):
    m = 0.511*10**6
    gamma = np.mean(getE(beam))/m
    beta = np.sqrt(1. - 1/gamma**2)
    return gamma * beta * getEmittance(beam, axis)

def getBunchKoef(beam, k, fixed='z'):
    if fixed == 'z':
        phi = -k*0.3*beam[:,8]
    elif fixed == 't':
        phi = k*beam[:,2]
    return np.abs(np.mean(np.exp(1.j*phi)))

def get_v(beam):
    E0 = getE(beam)

    m = 0.511*10**6
    gamma = E0/m
    beta = np.sqrt(1. - 1/gamma**2)
    return 3e8*beta

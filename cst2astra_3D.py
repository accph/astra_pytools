
import numpy as np 
import matplotlib.pyplot as plt

def format_function(row):
    format_row = []
    for x in row:
        if x > 0 and x < 1e-2:
            fmt_res = '%.8f' % x
        else:
            fmt = '%.6f' % x
            fmt_res = '%.6f' % x
            for char in fmt[::-1]:
                if char is '0':
                    fmt_res = fmt_res[:-1]
                else:
                    if char == '.':
                        fmt_res = fmt_res[:-1]

                    if fmt_res == '-0':
                        fmt_res = '0'
                    break

        format_row.append(fmt_res)
    return format_row

def get_data(filename, skiprows=0):
    data = np.loadtxt(filename, skiprows=skiprows)
    Z, Y, X = data[:,0], data[:,1], data[:,2]
    Fx, Fy, Fz = data[:,3], data[:,3], data[:,3]

    nx = len(X[(Y==Y[0]) * (Z==Z[0])])
    ny = len(Y[(Z==Z[0]) * (X==X[0])])
    nz = len(Z[(X==X[0]) * (Y==Y[0])])

    X = np.reshape(X, (nz, ny, nx))
    Y = np.reshape(Y, (nz, ny, nx))
    Z = np.reshape(Z, (nz, ny, nx))
    Fx = np.reshape(Fx, (nz, ny, nx))
    Fy = np.reshape(Fy, (nz, ny, nx))
    Fz = np.reshape(Fz, (nz, ny, nx))
    
    return X, Y, Z, Fx, Fy, Fz


if __name__ == '__main__':
    X, Y, Z, Fx, Fy, Fz = get_data('dipole_300AT_XZ.dat', skiprows=2)
    Fx, Fy, Fz = -Fx, -Fy, -Fz
    
    x, y, z = X[0,0,:], Y[0,:,0], Z[:,0,0]

    print(f'By_max : {np.max(Fy)}');

    #symmetry relative to Z=0 and X=0 planes
    '''
    print(f'x0 = {x[len(x)//2]} and z0 = {z[len(z)//2]}')
    for F in [Fx, Fy, Fx]:
        for k in range(len(x)//2):
            F[:,:,k] = F[:,:,-k-1]
            
        for k in range(len(z)//2):
            F[k,:,:] = F[-k-1,:,:]
    '''     
    #plt.pcolor(Z[:,:,len(x)//2], Y[:,:,len(x)//2], Fy[:,:,len(x)//2])
    plt.figure()
    plt.pcolor(X[:,len(y)//2,:], Z[:,len(y)//2,:], Fy[:,len(y)//2,:])
    plt.colorbar()

    plt.figure()
    for k, _ in enumerate(z):
        plt.plot(X[k,len(y)//2,:], Fy[k,len(y)//2,:])
    plt.show()
    '''
    Fx = np.reshape(Fx, (len(y)*len(z), len(x)))
    Fy = np.reshape(Fy, (len(y)*len(z), len(x)))
    Fz = np.reshape(Fz, (len(y)*len(z), len(x)))

    for F, axis_name in zip([Fx, Fy, Fz],['bx', 'by', 'bz']):
        with open(f'3D_dipole4RFgun.{axis_name}', 'w') as file:
            file.write(str(len(x)) + ' ' + ' '.join(format_function(x)) + ' \n')
            file.write(str(len(y)) + ' ' + ' '.join(format_function(y)) + ' \n')
            file.write(str(len(z)) + ' ' + ' '.join(format_function(z)) + ' \n')

            for u in range(len(F[:,0])):
                file.write(' '.join(format_function(F[u,:])) + '\n')
    
    print('done!')
    '''
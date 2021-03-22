
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
                if char == '0':
                    fmt_res = fmt_res[:-1]
                else:
                    if char == '.':
                        fmt_res = fmt_res[:-1]

                    if fmt_res == '-0':
                        fmt_res = '0'
                    break

        format_row.append(fmt_res)
    return format_row

def writeField(filename, x, y, z, F):
    header = str(len(x)) + ' ' + ' '.join(f'{e:.3f}' for e in x) + ' \n' \
           + str(len(y)) + ' ' + ' '.join(f'{e:.3f}' for e in y) + ' \n' \
           + str(len(z)) + ' ' + ' '.join(f'{e:.5f}' for e in z)

    np.savetxt(filename, F.reshape((len(z)*len(y),len(x))), fmt='%.5e', \
                header=header, comments='')
    
def get_data(filename, skiprows=0):
    data = np.loadtxt(filename, skiprows=skiprows)

    for n in range(3):
        data = data[np.argsort(data[:,n], kind='stable'),:]

    X, Y, Z = data[:,0], data[:,1], data[:,2]
    Fx, Fy, Fz = data[:,3], data[:,4], data[:,5]
    
    nx = len(X[(Y==Y[0]) * (Z==Z[0])])
    ny = len(Y[(Z==Z[0]) * (X==X[0])])
    nz = len(Z[(X==X[0]) * (Y==Y[0])])
    
    print(f'nx={nx}, ny={ny}, nz={nz}')

    X = np.reshape(X, (nz, ny, nx))
    Y = np.reshape(Y, (nz, ny, nx))
    Z = np.reshape(Z, (nz, ny, nx))
    Fx = np.reshape(Fx, (nz, ny, nx))
    Fy = np.reshape(Fy, (nz, ny, nx))
    Fz = np.reshape(Fz, (nz, ny, nx))

    return 1.e-3*X, 1.e-3*Y, 1.e-3*Z, Fx, Fy, Fz


if __name__ == '__main__':
    X, Y, Z, Fx, Fy, Fz = get_data('B-Field [Ms]__all.txt', skiprows=2)
    Fx, Fy, Fz = -Fx, -Fy, -Fz
    
    #import pdb; pdb.set_trace()

    z, y, x = Z[:,0,0], Y[0,:,0], X[0,0,:]
    ny = len(y)//2
    print(f'y = {Y[0,ny,0]}')

    plt.figure()
    plt.pcolor(Z[:,ny,:], X[:,ny,:], Fy[:,ny,:])
    plt.colorbar()

    ny0 = len(y)//2
    nz0 = len(z)//2
    nx0 = len(x)//2
    print(f'y = {y[ny0]}, z = {z[nz0]}, x = {x[nx0]}')
    print(f'max of By on axis: {np.max(Fy[:, ny0, nx0])} T')


    plt.figure()
    for k, _ in enumerate(x):
        plt.plot(Z[:,ny,k], Fy[:,ny,k])
    plt.show()

    writeField('3D_quad4RFgun_ky.bx', x, y, z, Fx)
    writeField('3D_quad4RFgun_ky.by', x, y, z, Fy)
    writeField('3D_quad4RFgun_ky.bz', x, y, z, Fz)
    
    '''
    for F, axis_name in zip([Fx, Fy, Fz],['bx', 'by', 'bz']):
        F = np.reshape(F, (len(y)*len(z), len(x)))

        with open(f'3D_dipole4RFgun.{axis_name}', 'w') as file:
            file.write(str(len(x)) + ' ' + ' '.join(format_function(x)) + ' \n')
            file.write(str(len(y)) + ' ' + ' '.join(format_function(y)) + ' \n')
            file.write(str(len(z)) + ' ' + ' '.join(format_function(z)) + ' \n')

            for row in F:
                file.write(' '.join(format_function(row)) + '\n')
    '''
    print('done!')

import numpy as np
import colorsys
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
from PyAstronomy import pyasl

def get_SysVars(h1, h2, b, n_frames):
    # get mass, age, temperature, radius data for each star
    M1 = h1.star_mass # in solar units
    t1 = h1.star_age # in years
    R1 = 10.**h1.log_R # in solar units
    T1 = 10.**h1.log_Teff

    M2 = h2.star_mass
    t2 = h2.star_age
    R2 = 10.**h2.log_R
    T2 = 10.**h2.log_Teff

    # system variables
    M_dot = b.lg_mtransfer_rate
    M1_dot = h1.lg_mstar_dot_1
    M2_dot = h2.lg_mstar_dot_2

    M1_interp = interp1d(t1, M1, fill_value="extrapolate")
    R1_interp = interp1d(t1, R1, fill_value="extrapolate")
    T1_interp = interp1d(t1, T1, fill_value="extrapolate")

    M2_interp = interp1d(t2, M2, fill_value="extrapolate")
    R2_interp = interp1d(t2, R2, fill_value="extrapolate")
    T2_interp = interp1d(t2, T2, fill_value="extrapolate")

    # timestep algo
    t_mt1 = M1 / abs(M1_dot)
    t_mt2 = M2 / abs(M2_dot)
    t_mtmin1 = min(t_mt1)
    t_mtmin2 = min(t_mt2)
    if t_mtmin1 < t_mtmin2:
        t = t1
    else:
        t = t2
    t = t[(t >= max(t1[0], t2[0])) & (t <= min(t1[-1], t2[-1]))]

    t_mt1 = np.interp(t, t1, t_mt1)
    t_mt2 = np.interp(t, t2, t_mt2)

    df = np.maximum( np.minimum(t_mt1[:-1], t_mt2[:-1])/(t[1:]-t[:-1]), np.ones(len(t)-1) )
    df = df.astype(np.int)

    t_remap = [t[0]]
    j = 0
    for i in range(len(t)-1):
        if i+1 >= j+df[i]:
            t_remap.append(t[i+1])
            j = i+1
    t_remap = np.array(t_remap)

    f_frame = np.linspace(0, 1, len(t_remap))

    tremap_interp = interp1d(f_frame, t_remap)
    fnew_frame = np.linspace(0, 1, n_frames)
    t_uniform = tremap_interp(fnew_frame)

    # rescaling all system variables on t_uniform
    M1 = M1_interp(t_uniform)
    R1 = R1_interp(t_uniform)
    T1 = T1_interp(t_uniform)

    M2 = M2_interp(t_uniform)
    R2 = R2_interp(t_uniform)
    T2 = T2_interp(t_uniform)

    a = b.binary_separation
    t = b.age

    a_interp = interp1d(t, a, fill_value="extrapolate")

    a = a_interp(t_uniform)

    return t_uniform, M1, M2, R1, R2, T1, T2, a

def get_MassRatio(m1, m2, i):
    # input mass array for star 1 and 2 to return mass ratio for a given index
    offset = -1*(np.shape(m1)[0] - np.shape(m2)[0])
    if m1[offset] > m2[i]:
        q = m2[i]/m1[offset]
        return q
    elif m1[offset] < m2[i]:
        q = m1[offset]/m2[i]
        return q

def get_LagrangePoints(q):
    # Positions (and potentials) of Lagrange points
    l1, l1pot = pyasl.get_lagrange_1(q)
    l2, l2pot = pyasl.get_lagrange_2(q)
    l3, l3pot = pyasl.get_lagrange_3(q)
    l4, l5 = pyasl.get_lagrange_4(), pyasl.get_lagrange_5()
    
    return l1, l2, l3, l4, l5

def get_LagrangePotential(q):
    # Positions (and potentials) of Lagrange points
    l1, l1pot = pyasl.get_lagrange_1(q)
    l2, l2pot = pyasl.get_lagrange_2(q)
    l3, l3pot = pyasl.get_lagrange_3(q)
    l4, l5 = pyasl.get_lagrange_4(), pyasl.get_lagrange_5()
    
    # Potential for l4 and l5 aren't included in the methods above. Need to get them separately.
    l4pot = pyasl.rochepot_dl(l4[0], l4[1], l4[2], q)
    l5pot = pyasl.rochepot_dl(l5[0], l5[1], l5[2], q)
    
    return l1pot, l2pot, l3pot, l4pot, l5pot

def create_PotentialGrid(l2, l3, l4, l5, q):
    # Getting potential meshgrid
    x, y = np.linspace(l3*(1.45+q), l2*(1+q), 300), np.linspace(l5[1]*2, l4[1]*2, 300)
    xx, yy = np.meshgrid(x, y)
    
    # Coordinates in orbital plane
    z = 0
    
    # Get dimensional values of Roche potential
    p = pyasl.rochepot_dl(xx, yy, z, q)
    
    # To get the extent vector
    ext_vect = [x[0], x[-1], y[0], y[-1]]
    
    return p, ext_vect

def label_StarAge(age_y):
    label = ''
    if age_y >= 1e6 and age_y < 1e9:
        label = 'Star Age: ' + str(round(age_y / 1e6, 3)) + ' Myr'
    elif age_y >= 1e9:
        label = 'Star Age: ' + str(round(age_y / 1e9, 3)) + ' Gyr'
    else:
        label = 'Star Age: ' + str(round(age_y, 3)) + ' yr'
        
    return label

def color_Temperature(T):
    # initializing spectral classes
    O5 = [54000, 157, 180, 255]
    B1 = [23000, 162, 185, 255]
    B3 = [17600, 167, 188, 255]
    B5 = [15200, 170, 191, 255]
    B8 = [12300, 175, 195, 255]
    A1 = [9330, 186, 204, 255]
    A3 = [8750, 192, 209, 255]
    A5 = [8310, 202, 216, 255]
    F0 = [7350, 228, 232, 255]
    F2 = [7050, 237, 238, 255]
    F5 = [6700, 251, 248, 255]
    F8 = [6300, 255, 249, 249]
    G2 = [5800, 255, 245, 236]
    G5 = [5660, 255, 244, 232]
    G8 = [5440, 255, 241, 223]
    K0 = [5240, 255, 235, 209]
    K4 = [4600, 255, 215, 174]
    K7 = [4000, 255, 198, 144]
    M2 = [3600, 255, 190, 127]
    M4 = [3400, 255, 187, 123]
    M6 = [3100, 255, 187, 123]
    
    T_range = np.array([54000, 23000, 17600, 15200, 12300,9330, 8750, 8310, 7350, 7050, 6700, 6300, 5800, 5660, 5440, 5240, 4600, 4000, 3600, 3400, 3100])
    R = np.array([157, 162, 167, 170, 175, 186, 192, 202, 228, 237, 251, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]) / 255
    G = np.array([180, 185, 188, 191, 195, 204, 209, 216, 232, 238, 248, 249, 245, 244, 241, 235, 215, 198, 190, 187, 187]) / 255
    B = np.array([255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 249, 236, 232, 223, 209, 174, 144, 127, 123, 123]) / 255
    
    HSV = []
    
    for i in range(len(T_range)):
        HSV.append(list(colorsys.rgb_to_hsv(R[i], G[i], B[i])))
        HSV[i][1] = min([HSV[i][1]*2, 1]) # via Professor
        
    R = []
    G = []
    B = []
    
    for i in range(len(HSV)):
        r, g, b = colorsys.hsv_to_rgb(HSV[i][0], HSV[i][1], HSV[i][2])
        R.append(r)
        G.append(g)
        B.append(b)
        
    len(HSV)
    ### END EDIT 10/8/21 ###
    
    # interpolating color with temperature
    r = interp1d(T_range, R, fill_value="extrapolate")
    g = interp1d(T_range, G, fill_value="extrapolate")
    b = interp1d(T_range, B, fill_value="extrapolate")
    
    # using spectral type-temperature relation for Main Sequence stars as approximation
    return r(T), g(T), b(T)
    
def plot_RocheLobe(fig, ax, lpoints, lpot, p, R1, R2, a, t, ext_vect, c1, c2, q):
    l1, l2, l3, l4, l5 = lpoints
    ax[0].contour(p, [lpot[3]*1.02, lpot[2], lpot[1], lpot[0]], cmap='Greys', extent=ext_vect) # scaled axis in terms of the Lagrange points
    ax[0].text(l1, 0, 'L1', horizontalalignment='center')
    ax[0].text(l2, 0, 'L2', horizontalalignment='center')
    ax[0].text(l3, 0, 'L3', horizontalalignment='center')
    ax[0].text(l4[0], l4[1], 'L4', horizontalalignment='center')
    ax[0].text(l5[0], l5[1], 'L5', horizontalalignment='center')
    
    RL1 = pyasl.roche_lobe_radius_eggleton(q, 1)
    RL2 = pyasl.roche_lobe_radius_eggleton(q, 2)
    
    draw_star1 = plt.Circle((0, 0), min(R1/a, RL1), color=c1)
    draw_star2 = plt.Circle((1, 0), min(R2/a, RL2), color=c2)
    ax[0].add_artist(draw_star1)
    ax[0].add_artist(draw_star2)
    ax[0].axis('equal')
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax[0].text(0.015, 0.98, label_StarAge(t), transform=ax[0].transAxes, fontsize=10, verticalalignment='top', bbox=props)
    ax[0].set_xlabel('x/a')
    ax[0].set_ylabel('y/a')
    ax[0].set_title('Roche Lobe Geometry')

def plot_MassvTime(fig, ax, t, M1, M2, title, savedir, i):
    # plot total mass of both star 1 and 2 against time
    ax[1].scatter(t[-1]-t[:i], M1[:i], label='Primary', s=15, c='black', marker='.')
    ax[1].scatter(t[-1]-t[:i], M2[:i], label='Secondary', s=15, c='blue', marker='.')
    ax[1].set_xlim(t[-1]-t[0], t[-1]-t[-2]) 
    ax[1].set_ylim(int(min(M1)*.8), int(max(M1)*1.8))
    ax[1].set_xscale('log')
    ax[1].set_title('Stellar Mass vs. Time')
    ax[1].set_xlabel('Time Before End (Years)')
    ax[1].set_ylabel('Mass ($M_\odot$)')
    ax[1].legend(loc='lower left')
    fig.tight_layout(pad=2)
    plt.savefig(savedir + title)
    plt.close()

def create_Snapshot(M1, M2, R1, R2, T1, T2, a, t_uniform, file, n_frames):
    # creating snapshots
    for i in range(n_frames):
        # get color data for each star
        c1 = np.array(color_Temperature(T1[i])).tolist()
        c2 = np.array(color_Temperature(T2[i])).tolist()
        
        q = get_MassRatio(M1, M2, i)
        
        if q <= 1.:
            lpoints = l1, l2, l3, l4, l5 = get_LagrangePoints(q)
            lpot = get_LagrangePotential(q)
            p, ext_vect = create_PotentialGrid(l2, l3, l4, l5, q)
        else:
            lpoints = l1, l2, l3, l4, l5 = get_LagrangePoints(1./q)
            lpot = get_LagrangePotential(1./q)
            p, ext_vect = create_PotentialGrid(l2, l3, l4, l5, 1./q)
            np.fliplr(p) 
            lpoints = list(lpoints)
            lpoints[3] = list(lpoints[3])
            lpoints[4] = list(lpoints[4])
            lpoints[0] = -lpoints[0]
            lpoints[1] = -lpoints[1]
            lpoints[2] = -lpoints[2]
            lpoints[3][0] = -lpoints[3][0]
            lpoints[4][0] = -lpoints[4][0]
        
        fig, ax = plt.subplots(2, gridspec_kw={'height_ratios': [4, 4]}, figsize=(6, 8))
        plot_RocheLobe(fig, ax, lpoints, lpot, p, R1[i], R2[i], a[i], t_uniform[i], ext_vect, c1, c2, q)
        title = 'PLOT_' + str(i)
        plot_MassvTime(fig, ax, t_uniform, M1, M2, title, '/Users/sean/Documents/Ricker_Research/' + file + '/PNGS/', i)
        print('Snapshot: ' + str(i) + '/' + str(n_frames))
        if i == n_frames - 1:
            print('Finished gathering snapshots')

def create_SnapshotTitles(n_frames):
    # creating snapshot titles
    plot_names = []

    for i in range(n_frames):
        if i == 0:
            continue
        else:
            plot_names.append('PLOT_' + str(i) + '.png')

    return plot_names


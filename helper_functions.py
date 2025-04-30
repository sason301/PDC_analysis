import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from time import sleep
from loaders import read_nxs_scan
import tqdm


def generate_tth(theta_d):
    merlin_pixs = np.arange(515) - 515 / 2
    tth = -merlin_pixs * 55e-3 / 1310 * 180 / np.pi
    return tth + theta_d


def initialize_opts(opts, ini_vals=None):
    if not ini_vals == None:
        for key in ini_vals.keys():
            if not key in opts.keys():
                opts[key] = ini_vals[key]

    if not 'mod' in opts: opts['mod'] = '2D'
    if not 'bkg' in opts: opts['bkg'] = None
    if not 'return' in opts: opts['return'] = True
    if not 'show' in opts: opts['show'] = False
    if not 'log' in opts: opts['log'] = False

    return opts


def show(scan_data, t=0.001):
    imgs = scan_data['imgs']
    plt.figure(num=9999)
    for jj in range(imgs.shape[2]):
        plt.imshow(imgs[:, :, jj])
        plt.title(jj)
        plt.show()
        sleep(t)
    plt.close(9999)


def bkg(imgs, bkg_area=0):
    if bkg_area == 0:
        bkg_area = [0, 100, 0, 100]
    elif bkg_area == 1:
        bkg_area = [400, 440, 320, 380]
    elif bkg_area == 2:
        bkg_area = [200, 430, 320, 380]
    bkg = imgs[bkg_area[0]:bkg_area[1], bkg_area[2]:bkg_area[3], :].mean(axis=(0, 1))
    return bkg


# %%% generate Θ - E curve

def show_roi(roi, scan_data=None, show=True):
    '''
    plots the roi on the 2D image from the detector
    '''
    if show == True:
        horiz_top_line = [[roi[0] - roi[2], roi[0] + roi[2]], [roi[1] - roi[3], roi[1] - roi[3]]]
        horiz_bot_line = [[roi[0] - roi[2], roi[0] + roi[2]], [roi[1] + roi[3], roi[1] + roi[3]]]
        vert_left_line = [[roi[0] - roi[2], roi[0] - roi[2]], [roi[1] - roi[3], roi[1] + roi[3]]]
        vert_right_line = [[roi[0] + roi[2], roi[0] + roi[2]], [roi[1] - roi[3], roi[1] + roi[3]]]
        plt.plot(horiz_top_line[0], horiz_top_line[1], '--', color='red')
        plt.plot(horiz_bot_line[0], horiz_bot_line[1], '--', color='red')
        plt.plot(vert_left_line[0], vert_left_line[1], '--', color='red')
        plt.plot(vert_right_line[0], vert_right_line[1], '--', color='red')

    if not scan_data == None:
        roi_width = -scan_data['theta_d'][roi[1] + roi[3]] + scan_data['theta_d'][roi[1] - roi[3]]
        if show == True:
            plt.text(roi[0] - 200, roi[1], 'theta_d_roi = ' + str(np.round(scan_data['theta_d'][roi[1]], 3))
                     , color='red', fontsize=15)
            plt.text(roi[0] - 200, roi[1] + 20, 'roi_width = ' + str(np.round(roi_width, 3))
                     , color='red', fontsize=15)
        return {'center_roi': scan_data['theta_d'][roi[1]], 'roi_width': roi_width}


def show_Braggs(idler_energy=0, delta=0):
    # n lambda = 2 d sin
    # E (eV) = 1239.8 / l (nm)
    h, k, l = 3, 0, 0
    d = 6.02 / np.sqrt(h ** 2 + k ** 2 + l ** 2)

    beam_energy = 10e3
    signal_energy = beam_energy - idler_energy

    beam_wavelength = 10 * 1239.8 / beam_energy
    signal_wavelength = 10 * 1239.8 / signal_energy

    Bragg = np.arcsin(beam_wavelength / 2 / d) * 180 / np.pi  # bragg angle (deg)
    Bragg_signal_energy = np.arcsin(signal_wavelength / 2 / d) * 180 / np.pi

    mu_Bragg = np.arange(-0.15, 0.15, 0.01) + Bragg
    tth_Bragg = 2 * (np.arange(-0.15, 0.15, 0.01) + Bragg) + delta

    mu_Bragg_sig = np.arange(-0.15, 0.15, 0.01) + Bragg
    tth_Bragg_sig = 2 * (np.arange(-0.15, 0.15, 0.01) + Bragg_signal_energy) + delta

    plt.plot(mu_Bragg, tth_Bragg, '--', color='red');
    plt.plot(mu_Bragg_sig, tth_Bragg_sig, '--', color='black')

    print(Bragg)
    print(Bragg_signal_energy)


def Gauss(x, A, mu, sig):
    y = A * np.exp(-1 * (x - mu) ** 2 / sig ** 2)
    return y


def find_peak_params(rc, show=True, separate_bragg=True, bragg_loc=None, bragg_width=None):
    if separate_bragg:
        bragg_index = np.argmin(np.abs(rc['axis'] - bragg_loc))
        d_theta = rc['axis'][1] - rc['axis'][0]
        peak_index = [bragg_index - int(bragg_width / (2 * d_theta)), bragg_index + int(bragg_width / (2 * d_theta))]
        bragg_x = rc['axis'][peak_index[0]:peak_index[1]]
        bragg_y = rc['RC'][peak_index[0]:peak_index[1]]
        bragg_params, _ = curve_fit(Gauss, bragg_x,bragg_y,p0=[bragg_y.max(), bragg_x.mean(),bragg_x[-1] - bragg_x[0]])
        I = bragg_params[0]
        mu = bragg_params[1]
        sig = bragg_params[2]

        bragg_fit = Gauss(rc['axis'], I, mu, sig)
        if show == True:
            if separate_bragg:
                plt.plot(bragg_x, bragg_fit, 'o', label='data')
            plt.plot(rc['axis'][peak_index[0]:peak_index[1]], fit_y, '-', label='fit')
            plt.text(rc['axis'][0], I, 'peak_I = ' + str(np.round(I)))
            plt.text(rc['axis'][0], I - 250, 'peak_pos = ' + str(np.round(mu, 4)))
            plt.text(rc['axis'][0], I - 500, 'peak_width = ' + str(np.round(sig, 5)))
    else:
        parameters, _ = curve_fit(Gauss, rc['axis'], rc['RC'], p0=[rc['RC'].max(), rc['axis'].mean(), 0.1])
        I = parameters[0]
        mu = parameters[1]
        sig = parameters[2]

        fit_y = Gauss(rc['axis'], I, mu, sig)
        # plt.plot(rc['axis'], rc['RC'], 'o', label='data')
        if show == True:
            plt.plot(rc['axis'], fit_y, '-', label='fit')
            plt.text(rc['axis'][0], I, 'peak_I = ' + str(np.round(I)))
            plt.text(rc['axis'][0], I - 250, 'peak_pos = ' + str(np.round(mu, 4)))
            plt.text(rc['axis'][0], I - 500, 'peak_width = ' + str(np.round(sig, 5)))
        return parameters


def imshow_snapshot_roi(roi, scan_data, snapshot):
    x, y, h, w = roi
    plt.imshow(scan_data['imgs'][y - h:y + h, x - w:x + w, snapshot])


def i16_roi_to_roi(i16_roi):  # center_roi=[cen_x,cen_y,width,height]
    x, y, h, w = i16_roi
    roi = [
        int(i16_roi[1]),
        int(i16_roi[0]),
        int(i16_roi[3] / 2),
        int(i16_roi[2] / 2)
    ]  # roi = [start_x,start,y,width,height]
    return roi

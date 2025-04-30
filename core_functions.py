import matplotlib.pyplot as plt
from loaders import get_exp_folder
from helper_functions import generate_tth, bkg, initialize_opts, show_roi, find_peak_params
from PIL import Image
import numpy as np


def read_scan(scan_num, folder=get_exp_folder(), load_imgs=True):
    '''
    this function loads all the data from a single scan
    input:
        scan_num - 4 last digits from the scan number
        load_imgs - True to load everything (including the detector images), False to load only the scan parametes
    return:
        a dict. with all the data
    '''
    return read_dat_scan(scan_num, folder, load_imgs=load_imgs)


'''
read scan from dat file
returns a dict with the data

ic1monitor is the io
'''


def read_dat_scan(scan_num, folder=get_exp_folder(), load_imgs=True):
    name = folder + str(105) + str(scan_num) + '.dat'
    data_lines = open(name, 'r').readlines()

    ind = data_lines.index(' &END\n') + 1
    num_of_points = len(data_lines) - ind - 1

    scan_parameters = data_lines[ind].split()

    if 'merlin' in data_lines[ind - 3]:
        img_ind = data_lines[ind - 3][22:-2]
    elif 'pilatus3' in data_lines[ind - 3]:
        img_ind = data_lines[ind - 3][29:-2]

    scan_data = {}
    scan_data['atten'] = int(data_lines[128][6:-1])
    scan_data['transmission'] = float(data_lines[129][13:-1])
    scan_data['gamma'] = float(data_lines[28][4:-1])
    scan_data['theta_d'] = generate_tth(scan_data['gamma'])
    scan_data['thp'] = float(data_lines[49][4:-1])

    for n in scan_parameters:
        scan_data[n] = []

    scan_cmd = [l for l in data_lines if 'cmd=' in l][0]
    scan_cmd_inds = [10, 10 + scan_cmd[10:].find(' ')]
    scan_data['scanning_motor'] = scan_parameters[0]

    if load_imgs == True:
        images = []
        for j in range(num_of_points):
            images.append(img_ind.replace('%05d', "{:05d}".format(j + 1)))

        if 'merlin' in data_lines[ind - 3]:
            scan_data['imgs'] = np.zeros([515, 515, len(images)])
        elif 'pilatus3' in data_lines[ind - 3]:
            scan_data['imgs'] = np.zeros([195, 487, len(images)])

        for jj, img in enumerate(images):
            scan_data['imgs'][:, :, jj] = np.array(Image.open(folder + img))

        if 'merlin' in data_lines[ind - 3]:
            scan_data['bkg_0'] = bkg(scan_data['imgs'])
            scan_data['bkg_1'] = bkg(scan_data['imgs'], bkg_area=1)
            scan_data['bkg_2'] = bkg(scan_data['imgs'], bkg_area=2)

    for d in data_lines[ind + 1:]:
        s = d.split()
        for nn, n in enumerate(scan_parameters):
            try:
                scan_data[n].append(float(s[nn]))
            except:
                scan_data[n].append(s[nn])

    return scan_data


'''
read scan from dat file
returns a dict with the data

ic1monitor is the io
'''


def read_dat_scan(scan_num, folder=get_exp_folder(), load_imgs=True):
    name = folder + str(105) + str(scan_num) + '.dat'
    data_lines = open(name, 'r').readlines()

    ind = data_lines.index(' &END\n') + 1
    num_of_points = len(data_lines) - ind - 1

    scan_parameters = data_lines[ind].split()

    if 'merlin' in data_lines[ind - 3]:
        img_ind = data_lines[ind - 3][22:-2]
    elif 'pilatus3' in data_lines[ind - 3]:
        img_ind = data_lines[ind - 3][29:-2]

    scan_data = {}
    scan_data['atten'] = int(data_lines[128][6:-1])
    scan_data['transmission'] = float(data_lines[129][13:-1])
    scan_data['gamma'] = float(data_lines[28][4:-1])
    scan_data['theta_d'] = generate_tth(scan_data['gamma'])
    scan_data['thp'] = float(data_lines[49][4:-1])

    for n in scan_parameters:
        scan_data[n] = []

    scan_cmd = [l for l in data_lines if 'cmd=' in l][0];
    scan_cmd_inds = [10, 10 + scan_cmd[10:].find(' ')]
    scan_data['scanning_motor'] = scan_parameters[0]

    if load_imgs == True:
        images = []
        for j in range(num_of_points):
            images.append(img_ind.replace('%05d', "{:05d}".format(j + 1)))

        if 'merlin' in data_lines[ind - 3]:
            scan_data['imgs'] = np.zeros([515, 515, len(images)])
        elif 'pilatus3' in data_lines[ind - 3]:
            scan_data['imgs'] = np.zeros([195, 487, len(images)])

        for jj, img in enumerate(images):
            scan_data['imgs'][:, :, jj] = np.array(Image.open(folder + img))

        if 'merlin' in data_lines[ind - 3]:
            scan_data['bkg_0'] = bkg(scan_data['imgs'])
            scan_data['bkg_1'] = bkg(scan_data['imgs'], bkg_area=1)
            scan_data['bkg_2'] = bkg(scan_data['imgs'], bkg_area=2)

    for d in data_lines[ind + 1:]:
        s = d.split()
        for nn, n in enumerate(scan_parameters):
            try:
                scan_data[n].append(float(s[nn]))
            except:
                scan_data[n].append(s[nn])

    return scan_data


# %%% generate Θ - 2Θ maps
def generate_th_tth(scan_data, roi, roi_range=[], opts={}):
    '''
    generates a Θ - 2Θ data from a single scan
    input:
        scan_data - data from the read_scan function
        roi - a list with 4 values [roi_x_center, roi_y_center, roi_width, roi_hight]. the actual width and hight of the roi is twice roi_width and roi_hight (one from each side)
        roi_range - (optional) required in order to generate a line plot of the peak positions for different ROIs on 2Θ
        opts -
            'bkg': normalize the RC with a pre defined background area on the detector
            'return': True to return the data, False to not return anything
            'show': True to plot the Θ - 2Θ map
            'mod': '2D' to generate a full Θ - 2Θ map
                   '1D' to generate a line plot with the peak position of the RC for different ROIs on 2Θ

    return:
        1D line data\ Θ - 2Θ map

    '''
    opts = initialize_opts(opts, {'bkg': None, 'return': True, 'show': False})

    imgs = scan_data['imgs']
    scan_map = {}

    if opts['bkg'] == True:
        imgs = imgs - bkg(imgs)

    if opts['mod'] == '2D':
        scan_map['map'] = imgs[:, roi[0] - roi[2]:roi[0] + roi[2], :].sum(axis=(1))
        scan_map['motor_x'] = scan_data['scanning_motor']
        scan_map['axis_x'] = np.array(scan_data[scan_data['scanning_motor']])
        scan_map['axis_y'] = scan_data['theta_d']
        scan_map['motor_y'] = 'Θ_d'

        if opts['show'] == True:
            plt.figure(figsize=[10, 10])
            if opts['log'] == True:
                plt.imshow(np.log(1 + scan_map['map']),
                           extent=[scan_map['axis_x'][0], scan_map['axis_x'][-1],
                                   scan_map['axis_y'][0], scan_map['axis_y'][-1]],
                           aspect='auto')
                plt.title(scan_map['motor_x'] + ' v.s. Θ_d (log I)', fontsize=20)
            else:
                plt.imshow(scan_map['map'],
                           extent=[scan_map['axis_x'][0], scan_map['axis_x'][-1],
                                   scan_map['axis_y'][0], scan_map['axis_y'][-1]],
                           aspect='auto')
                plt.title(scan_map['motor_x'] + ' v.s. Θ_d', fontsize=20)
            plt.xlabel(scan_map['motor_x'], fontsize=20)
            plt.ylabel(scan_map['motor_y'], fontsize=20)

        if opts['return'] == True:
            return scan_map

    if opts['mod'] == '1D' and not len(roi_range) == 0:

        scan_map['rocking_curves'] = []
        scan_map['2theta'] = scan_data['theta_d'][roi_range]
        scan_map['theta'] = np.empty(shape=len(roi_range))
        scan_map['width'] = np.empty(shape=len(roi_range))

        for jj, roi_2theta in enumerate(roi_range):
            roi[1] = roi_2theta
            rc = generate_RC(scan_data, roi=roi)
            scan_map['rocking_curves'].append(rc)
            scan_map['theta'][jj] = rc['peak_params'][1]
            scan_map['width'][jj] = rc['peak_params'][2]

        scan_map['fit'] = np.polyfit(scan_map['theta'], scan_map['2theta'], 1)

        if opts['show'] == True:
            plt.figure(figsize=[10, 10])
            plt.plot(scan_map['theta'], scan_map['2theta'])
            plt.xticks(fontsize=15);
            plt.yticks(fontsize=15)
            plt.ticklabel_format(useOffset=False, style='plain')
            plt.xlabel('theta', fontsize=20);
            plt.ylabel('2 theta', fontsize=20);
            plt.title('theta - 2 theta (peak position)', fontsize=20)

        if opts['return'] == True:
            return scan_map


def RC_over_time(scans, roi, roi_range=[], opts={}):
    '''
    generate RCs from a series of scans to show the time evolution
    input:
        scan numbers
        roi
        roi_range - to generate 1D Θ - 2Θ  maps
        opts
    return:
        a dict. with all the generated RCs and its parameters
    '''
    opts = initialize_opts(opts, {'mod': '1D', 'return': True, 'show': True})

    scans_overall_data = {}
    scans_overall_data['scan_numbers'] = scans
    scans_overall_data['rocking_curves'] = []
    scans_overall_data['time'] = np.empty(len(scans))
    scans_overall_data['peak_positions'] = np.empty(len(scans))
    scans_overall_data['peak_intensity'] = np.empty(len(scans))
    scans_overall_data['peak_width'] = np.empty(len(scans))
    scans_overall_data['theta_2theta'] = []

    for jj, scan_num in enumerate(scans):
        scan_data = read_scan(scan_num)
        rocking_curve = generate_RC(scan_data, roi)
        scans_overall_data['rocking_curves'].append(rocking_curve)
        scans_overall_data['peak_intensity'][jj] = rocking_curve['peak_params'][0]
        scans_overall_data['peak_positions'][jj] = rocking_curve['peak_params'][1]
        scans_overall_data['peak_width'][jj] = rocking_curve['peak_params'][2]
        scans_overall_data['time'][jj] = np.mean(scan_data['TimeSec'])

        if not len(roi_range) == 0:
            th_tth = generate_th_tth(scan_data, roi, roi_range, {'mod': '1D'})
            scans_overall_data['theta_2theta'].append([th_tth['theta'], th_tth['2theta']])

    if opts['show'] == True:
        fig, ax = plt.subplots(ncols=3)
        ax[0].plot(scans_overall_data['time'] - scans_overall_data['time'][0],
                   scans_overall_data['peak_intensity'], '--o', )
        ax[0].set_xlabel('time', fontsize=15);
        ax[0].set_ylabel('peak_intensity', fontsize=15);

        ax[1].plot(scans_overall_data['time'] - scans_overall_data['time'][0],
                   scans_overall_data['peak_positions'], '--o', )
        ax[1].set_xlabel('time', fontsize=15);
        ax[0].set_ylabel('peak_positions', fontsize=15);

        ax[2].plot(scans_overall_data['time'] - scans_overall_data['time'][0]
                   , scans_overall_data['peak_width'], '--o', )
        ax[2].set_xlabel('time', fontsize=15);
        ax[0].set_ylabel('peak_width', fontsize=15);

        if not len(roi_range) == 0:
            plt.figure()
            [plt.plot(th_tth[0], th_tth[1], label=scans[jj]) for jj, th_tth in
             enumerate(scans_overall_data['theta_2theta'])]
            plt.xticks(fontsize=15);
            plt.yticks(fontsize=15);
            plt.legend(fontsize=15)
            plt.ticklabel_format(useOffset=False, style='plain')
            plt.xlabel('theta', fontsize=20);
            plt.ylabel('2 theta', fontsize=20);
            plt.title('theta - 2 theta (peak position)', fontsize=20)

    if opts['return'] == True:
        return scans_overall_data


def generate_RC(scan_data, roi, opts={}):
    '''
    generates a rocking curve over a specific region of interest form the merlin/pil images
    input:
        scan_data - data from the read_scan function
        roi - a list with 4 values [roi_x_center, roi_y_center, roi_width, roi_hight]. the actual width and hight of the roi is twice roi_width and roi_hight (one from each side)
        opts -
            'bkg': normalize the RC with a pre defined background area on the detector
            'return': True to return the RC data, False to not return anything
            'show': True to plot the RC

    returns:
        a dict. with the RC data
        plots the RC

    '''
    opts = initialize_opts(opts, {'bkg': None, 'return': True, 'show': False})
    imgs = scan_data['imgs']

    if opts['bkg'] == None:
        imgs = imgs
    elif opts['bkg'] == 0:
        imgs = imgs - scan_data['bkg_0']
    elif opts['bkg'] == 1:
        imgs = imgs - scan_data['bkg_1']
    elif opts['bkg'] == 2:
        imgs = imgs - scan_data['bkg_2']

    x, y, w, h = roi

    rocking_curve = {}
    rocking_curve['integration_time'] = scan_data['count_time'][0]
    rocking_curve['RC'] = imgs[y - h:y + h, x - w:x + w, :].sum(axis=(0, 1)) / rocking_curve['integration_time']
    rocking_curve['motor'] = scan_data['scanning_motor']
    rocking_curve['axis'] = np.array(scan_data[scan_data['scanning_motor']])
    rocking_curve['attenuation'] = scan_data['atten']
    rocking_curve['transmission'] = scan_data['transmission']
    rocking_curve['roi'] = show_roi(roi, scan_data, show=False)
    rocking_curve['ion_chamber'] = scan_data['ic1monitor']
    rocking_curve['ring_current'] = scan_data['rc']
    try:
        rocking_curve['peak_params'] = find_peak_params({'axis': rocking_curve['axis'], 'RC': rocking_curve['RC']},
                                                        show=False)
    except:
        rocking_curve['peak_params'] = []

    if opts['show'] == True:
        plt.plot(rocking_curve['axis'], rocking_curve['RC'])
        plt.xlabel(rocking_curve['motor'] + ' (deg)')
        plt.ylabel('counts')

    if opts['return'] == True:
        return rocking_curve

def generate_RC_vs_time(scans, roi, opts={'bkg': 0, 'return': True, 'show': True, 'log': True}):
    opts = initialize_opts(opts)
    rocking_curves = []
    ax = []
    time = []

    for scan in scans:
        scan_data = read_dat_scan(scan)
        rc = generate_RC(scan_data, roi=roi, opts=opts)
        rocking_curves.append(rc)
        ax.append(rc['axis'])
        time.append(np.array(scan_data['TimeSec']).mean())
    if opts['return'] == True:
        return {'rocking_curves': rocking_curves, 'axis': ax, 'time': time}


'''
eval the bkg for each image  
'''

def generate_th_eneergy(scan_range, roi, opts={'bkg': True, 'return': True, 'show': True, 'log': False}):
    opts = initialize_opts(opts)

    scan_motor = [read_nxs_scan(n, load_imgs=False)['scanning_notor'] for n in scan_range]
    same_motor = all(s_m == 'mu' for s_m in scan_motor)

    scan_map = {}

    if same_motor == True:
        scan_map['energies'] = np.zeros(len(scan_range))

        scan_data = read_nxs_scan(scan_range[0])
        # roi = select_ROI(scan_data['imgs'][:, :, 0:3].sum(axis=2))
        scan_map['mu_ax'] = generate_RC(scan_data, roi=roi)['axis']
        scan_map['roi'] = roi

        scan_map['RC'] = []

        for jj, scan_num in enumerate(tqdm(scan_range)):
            scan_data = read_nxs_scan(scan_num)
            RC = generate_RC(scan_data, roi=roi, opts=opts)
            rc, rc_ax = [RC['RC'], RC['axis']]
            scan_map['RC'].append(np.interp(scan_map['mu_ax'], rc_ax, rc))
            scan_map['energies'][jj] = scan_data['E']

        scan_map['RC'] = np.stack(scan_map['RC'])

        if opts['show'] == True:
            plt.figure(num=99999)
            if opts['log'] == True:
                plt.imshow(np.log(1 + scan_map['RC']),
                           extent=[scan_map['mu_ax'][0], scan_map['mu_ax'][-1],
                                   scan_map['energies'][0], scan_map['energies'][-1]],
                           aspect='auto')
                plt.title('mu v.s. energy (log I)', fontsize=20)
            else:
                plt.imshow(scan_map['RC'],
                           extent=[scan_map['mu_ax'][0], scan_map['mu_ax'][-1],
                                   scan_map['energies'][0], scan_map['energies'][-1]],
                           aspect='auto')
                plt.title('mu v.s. energy', fontsize=20)
            plt.xlabel('mu', fontsize=20)
            plt.ylabel('energy', fontsize=20)
        if opts['return'] == True:
            return scan_map



from core_functions import *
from helper_functions import *

if __name__ == '__main__':
    scan_num = 6248
    scan_data = read_scan(scan_num)
    i16_roi = [300, 177, 20, 10]  # x y w h
    roi=i16_roi_to_roi(i16_roi)
    print(roi)
    plt.imshow(scan_data['imgs'][:, :, 20])
    show_roi(roi)
    opts = {'bkg': None, 'return': True, 'show': False, 'log': False}

    rc = generate_RC(scan_data, roi, opts=opts)
    plt.figure()
    plt.plot(rc['axis'], rc['RC'])
    find_peak_params(rc,separate_bragg = True,bragg_loc=28.226,bragg_width=0.08)
    plt.show()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

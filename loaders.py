
from nexusformat.nexus import *
from PIL import Image


def get_exp_folder():
    '''
    here you should insert the data folder
    '''
    return r'C:/Users/sason/1T-TaS2 pdc/'

def explain_motor(motor_name):
    """
    Returns an explanation for a given motor from the I16 beamline.
    the data is taken from ChatGPT

    Parameters:
        motor_name (str): The name of the motor (e.g., 'delta', 'gamma', 'phi').

    Returns:
        str: A description of the motor's function.
    """
    motor_descriptions = {
        'delta': "Controls the detector arm angle in the horizontal scattering plane, "
                 "adjusting the detector's position relative to the sample.",
        'gamma': "Controls the detector arm angle in the vertical scattering plane, "
                 "used for out-of-plane reflections or reciprocal space mapping.",
        'kappa': "Controls the kappa angle in the kappa geometry goniometer, allowing "
                 "flexible rotations of the sample without phi constraints.",
        'mu': "Adjusts the sample tilt angle in the horizontal plane, controlling "
              "the incident angle of the X-ray beam onto the sample.",
        'offsetdelta': "Applies a correction or offset to the delta motor, often to account "
                       "for beamline-specific geometrical shifts or detector alignment.",
        'phi': "Rotates the sample around an axis normal to its surface, fine-tuning "
               "its orientation in reciprocal space.",
        'theta': "Adjusts the sample rocking angle along the X-ray beam axis, enabling "
                 "alignment for diffraction experiments."
    }

    # Return the description if the motor is recognized, or a default message
    return motor_descriptions.get(
        motor_name.lower(),
        "Motor name not recognized. Please check the input or add a description for this motor."
    )
#%%%
# NEED TO ADD:
# pump energy, inpt energy, attenuation, monitor, hkl
# read the scan files from nxs files. Dont use this.
def read_nxs_scan(scan_num, folder=get_exp_folder(), load_imgs=True):
    name = folder + str(scan_num) + '.nxs'
    data = nxload(name)
    scan_data = {}

    if 'merlin' in list(data.entry1):
        detector_images = [mer[29:] for mer in list(data.entry1.instrument.merlin.image_data)]
        s1, s2 = [256, 256]
        scan = data.entry1.merlin
    elif 'pil100k' in list(data.entry1):
        detector_images = list(data.entry1.instrument.pil100k.image_data)
        scan = data.entry1.pil100k
        s1, s2 = [195, 487]

    scan_data['transmission'] = np.ones(len(list(scan['mu'])))  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    scan_parameters = list(scan)

    scan_cmd = str(data.entry1.scan_command);
    scan_cmd_inds = [5, 5 + scan_cmd[5:].find(' ')]
    scan_data['scanning_notor'] = scan_cmd[scan_cmd_inds[0]:scan_cmd_inds[1]]

    for n in scan_parameters:
        scan_data[n] = list(scan[n])

    if load_imgs == True:
        scan_data['imgs'] = np.zeros([s1, s2, len(detector_images)])

        for jj, d_i in enumerate(detector_images):
            scan_data['imgs'][:, :, jj] = scan_data['transmission'][jj] * np.array(
                Image.open(folder + d_i))  # the local files are stored in a different folder

    # dat_file = open(name[:-3]+'dat','r').readlines()
    # scan_data['hkl'] = [float(dat_file[jjj][2:-1]) for jjj in [30,31,32]]
    scan_data['E'] = 0
    return scan_data
# %%%
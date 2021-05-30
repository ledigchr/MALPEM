# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory

import os.path
import malpem.mytools

def N4(input_file, output_file, field_strength, input_mask, output_dir):
# DEFINITIONS
    binary_N4 = os.path.join(malpem.mytools.__malpem_path__, "lib", "itk", "N4")
# END DEFINITIONS

    task_name = "N4 bias correction"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_file, "")

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "N4-" + malpem.mytools.nifty_basename(input_file) + ".log")

    if input_mask == "":
        if field_strength == '1.5T':
            parameters_N4 = " -d 3 -i " + input_file + " -o " + output_file + " -s 2 -c [50x40x30x20,0.0000001] " \
                                                                              "-b [200,3,0.0,0.5] -t [0.15,0.01,200]"
        elif field_strength == '3T':
            parameters_N4 = " -d 3 -i " + input_file + " -o " + output_file + " -s 2 -c [50x40x30x20,0.0000001] " \
                                                                              "-b [75,3,0.0,0.5] -t [0.15,0.01,200]"
        else:
            print "Warning N4: Unknown field strength defaulting to 1.5T parameters"
            parameters_N4 = " -d 3 -i " + input_file + " -o " + output_file + " -s 2 -c [50x40x30x20,0.0000001] " \
                                                                              "-b [200,3,0.0,0.5] -t [0.15,0.01,200]"
    else:
        if field_strength == '1.5T':
            parameters_N4 = " -d 3 -i " + input_file + " -x " + input_mask + " -o " + output_file + " -s 2 " \
                            "-c [50x40x30x20,0.0000001] -b [200,3,0.0,0.5] -t [0.15,0.01,200]"
        elif field_strength == '3T':
            parameters_N4 = " -d 3 -i " + input_file + " -x " + input_mask + " -o " + output_file + " -s 2 " \
                            "-c [50x40x30x20,0.0000001] -b [75,3,0.0,0.5] -t [0.15,0.01,200]"
        else:
            print "Warning N4: Unknown field strength defaulting to 3T parameters"
            parameters_N4 = " -d 3 -i " + input_file + " -x " + input_mask + " -o " + output_file + " -s 2 " \
                            "-c [50x40x30x20,0.0000001] -b [75,3,0.0,0.5] -t [0.15,0.01,200]"

    malpem.mytools.execute_cmd(binary_N4, parameters_N4, logfile)
    malpem.mytools.ensure_file(output_file, "")

    malpem.mytools.finished_task(start_time, task_name)
    return True


def get_full_image_mask(input_file, output_file):
# DEFINITIONS
    binary_fsl = os.path.join(malpem.mytools.__malpem_path__, "lib", "niftyseg", "seg_maths")
# END
    task_name = "getting mask for full image"
    start_time = malpem.mytools.start_task(task_name)

    parameters_binarise = input_file + " -bin -add 1 -bin " + output_file
    malpem.mytools.execute_cmd(binary_fsl, parameters_binarise, "")
    malpem.mytools.ensure_file(output_file, "")

    malpem.mytools.finished_task(start_time, task_name)

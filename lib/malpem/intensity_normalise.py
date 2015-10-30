# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory

import os
import malpem.mytools


def robust_rescale(input_file, output_file, output_dir):
# DEFINITIONS
    binary_normalise = os.path.join(malpem.mytools.__malpem_path__, "lib", "scale")
# END DEFINITIONS
    task_name = "Robust intensity rescaling"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_file, "")
    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "normalise-" + malpem.mytools.nifty_basename(input_file) + ".log")

    parameters_normalise = input_file + " " + output_file + " " + output_dir

    #binary_normalise = os.path.join(malpem.mytools.__malpem_path__, 'bin/transformation')
    #parameters_normalise = input_file + " " + output_file
    malpem.mytools.execute_cmd(binary_normalise, parameters_normalise, logfile)

    malpem.mytools.ensure_file(output_file, "")
    malpem.mytools.finished_task(start_time, task_name)

    return True

# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory


import os
import malpem.mytools
import malpem.registration

def pincram(input_file, output_mask, threads, output_dir):
# DEFINITIONS
    binary_pincram = os.path.join(malpem.mytools.__malpem_path__, "lib", "pincram", "pincram-0.2.3_ireg.sh")
    a_pincram = os.path.join(malpem.mytools.__malpem_path__, "atlas", "pincram/")
#   tpn = os.path.join(malpem.mytools.__malpem_path__, "atlas", "pincram/neutral.dof.gz")
# END DEFINITIONS

    task_name = "pincram brain extraction"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_file, "")

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "pincram-" + malpem.mytools.nifty_basename(input_file) + ".log")

    tmp_dir = os.path.join(output_dir, "tmp_pincram/")
    malpem.mytools.check_ex_dir(tmp_dir)

    # This directory shouldn't exist so that pincram deletes all these large intermediate output files
    discard_dir = os.path.join(tmp_dir, "discard/")
    #malpem.mytools.check_ex_dir(discard_dir)   (IF UNCOMMENTED TEMPORARY PINCRAM FILES ARE KEPT)

    mni_dof = os.path.join(output_dir, "mni-" + malpem.mytools.nifty_basename(input_file) + ".dof.gz")
    if not os.path.isfile(mni_dof):
        malpem.registration.dof2mni(input_file, mni_dof, "rigid", output_dir)
    else:
        print "Skipping MNI alignment (" + mni_dof + "): file exists"

    parameters_pincram = input_file + " -result " + output_mask + " -tempbase " + tmp_dir + " -output " + discard_dir + \
                         " -atlas " + a_pincram + " -levels 3 -par " + threads + " -tpn " + mni_dof

    #binary_pincram = os.path.join(malpem.mytools.__malpem_path__, 'bin/transformation')
    #parameters_pincram = " " + input_file + " " + output_mask
    malpem.mytools.execute_cmd(binary_pincram, parameters_pincram, logfile)

    malpem.mytools.ensure_file(output_mask, "")
    malpem.mytools.finished_task(start_time, task_name)

    return True

def apply_mask(input_file, output_file, brain_mask):
# DEFINITIONS
    binary_apply_mask = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_apply_mask")
# END
    # APPLY BRAIN MASK
    task_name = "apply brain mask"
    start_time = malpem.mytools.start_task(task_name)

    parameters_apply_mask = " " + input_file + " " + output_file + " " + brain_mask

    malpem.mytools.execute_cmd(binary_apply_mask, parameters_apply_mask, "")

    malpem.mytools.ensure_file(output_file, "")
    malpem.mytools.finished_task(start_time, task_name)

    return True

def binarise(input_file, output_file):
# DEFINITIONS
    binary_fsl = os.path.join(malpem.mytools.__malpem_path__, "lib", "niftyseg", "seg_maths")
# END
    task_name = "binarising image for brain mask"
    start_time = malpem.mytools.start_task(task_name)

    parameters_binarise = input_file + " -bin " + output_file
    malpem.mytools.execute_cmd(binary_fsl, parameters_binarise, "")
    malpem.mytools.ensure_file(output_file, "")

    malpem.mytools.finished_task(start_time, task_name)

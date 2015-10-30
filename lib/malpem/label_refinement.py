# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory


import os
import malpem.mytools

mrf_low = 1.0
mrf_high = 2.5
gamma = -1

def malpem_refinement(input_file, priors_prob_base, output_malpem, output_prob_dir, output_dir):
# DEFINITIONS
    binary_MALPEMrefinement = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_malpem")
    mrf_parameter_file = os.path.join(malpem.mytools.__malpem_path__, "etc", "conn139_HC.mrf")
# END DEFINITIONS

    task_name = "MALPEM refinement"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_file, "")

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "MALPEM-" + malpem.mytools.nifty_basename(input_file) + ".log")

    tmp_dir = os.path.join(output_dir, "tmp_malpem/")
    malpem.mytools.check_ex_dir(tmp_dir)

    priors_dir = os.path.dirname(priors_prob_base)
    priors_count = len([curfile for curfile in os.listdir(priors_dir)
                                  if os.path.isfile(os.path.join(priors_dir, curfile))])

    priors_parameters = ""
    for i in range(priors_count):
        priors_parameters = priors_parameters + " " + priors_prob_base + "_" + str(i) + ".nii.gz"

    garbage = os.path.join(tmp_dir, "garbage.nii.gz")
    parameters_MALPEMrefinement = input_file + " " + str(priors_count) + " " + priors_parameters + " " + \
                                  output_malpem + " -mrf " + mrf_parameter_file + " " + \
                                  " -padding -1 -mrfweights " + str(mrf_low) + " " + str(mrf_high) + \
                                  " -combineWithPriors " + str(gamma) +  " -correctCSF -posteriors " + \
                                  output_prob_dir

    #binary_MALPEMrefinement = os.path.join(malpem.mytools.__malpem_path__, os.curdir), 'bin/transformation')
    #parameters_MALPEMrefinement = input_file + " " + output_malpem

    malpem.mytools.execute_cmd(binary_MALPEMrefinement, parameters_MALPEMrefinement, logfile)

    malpem.mytools.ensure_file(output_malpem, "")

    malpem.mytools.finished_task(start_time, task_name)

    return True

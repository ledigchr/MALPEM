# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory

import os
import intensity_normalise
import malpem.mytools

# Gaussian weighted fusion (SD of kernel)
sigma = 2.5

def lwf(input_file, a_images_scaled, a_labels, output_fusion, output_prob, output_dir):
# DEFINITIONS
    binary_labelfusion = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_gaussian_fusion")
# END DEFINITIONS

    task_name = "locally weighted label fusion"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_file, "")

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "fusion-" + malpem.mytools.nifty_basename(input_file) + ".log")

    if len(a_images_scaled) != len(a_labels):
        print "--- ERROR: number of atlas images/labels not identical ---"
        exit(1)

    a_count = len(a_images_scaled)
    a_parameters = ""
    for i in range(len(a_images_scaled)):
        a_parameters = a_parameters + " " + a_labels[i] + " " + a_images_scaled[i]

    tmp_dir = os.path.join(output_dir, "tmp_fusion/")
    malpem.mytools.check_ex_dir(tmp_dir)

    input_scaled = os.path.join(tmp_dir, malpem.mytools.nifty_basename(input_file) + "_scaled.nii.gz")

    if not os.path.isfile(input_scaled):
        intensity_normalise.robust_rescale(input_file, input_scaled, output_dir)
    else:
        print "Skipping intensity normalisation (" + input_scaled + "): file exists"

    parameters_labelfusion = input_scaled + " " + str(sigma) + " " + str(a_count) + " " + \
                             a_parameters + " " + output_prob + " " + output_fusion

    malpem.mytools.execute_cmd(binary_labelfusion, parameters_labelfusion, logfile)

    malpem.mytools.ensure_file(output_fusion, "")
    malpem.mytools.finished_task(start_time, task_name)

    return True


def create_tissue_seg(input_file, input_seg, output_seg, output_dir):
# DEFINITIONS
    binary_segmaths = os.path.join(malpem.mytools.__malpem_path__, "lib", "niftyseg", "seg_maths")

    # NMM STRUCTURE IDs FOR RESPECTIVE TISSUE CLASSES
    vent_list = [1, 2, 21, 22, 23, 24]
    cgm_list = range(41, 139, 1)
    dgm_list = range(1, 41, 1)
    wm_list = [12, 13, 16, 17]
    other_list = [14, 15, 18, 33, 34]
    for i in wm_list:
        dgm_list.remove(i)
    for i in vent_list:
        dgm_list.remove(i)
    for i in other_list:
        dgm_list.remove(i)
# END DEFINITIONS

    task_name = "creating tissue segmentation from structural segmentation"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(input_seg, "")

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "tissue-" + malpem.mytools.nifty_basename(input_file) + ".log")

    parameters_segmaths = input_seg + " -mul 0 " + output_seg
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    for i in vent_list:
        parameters_segmaths = input_seg + " -thr " + str(i-1) + " -uthr " + str(i+1) + " -bin -mul 1 -add " + \
                              output_seg + " " + output_seg
        malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

# DEEP GRAY MATTER, HANDLE CONSECUTIVE CLASSES SPECIAL TO ACCELERATE
    low = 0
    high = 0
    for i in dgm_list:
        if low == 0:
            low = i
        if high == 0:
            high = i
        elif high == i - 1:
            high = i
        else:
            parameters_segmaths = input_seg + " -thr " + str(low-1) + " -uthr " + str(high+1) + " -bin -mul 2 -add " + \
                                  output_seg + " " + output_seg
            malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)
            low = i
            high = i

    if low > 0:
        parameters_segmaths = input_seg + " -thr " + str(low-1) + " -uthr " + str(high+1) + " -bin -mul 2 -add " + \
                              output_seg + " " + output_seg
        malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)
# DONE DGM

# CORTICAL GRAY MATTER, HANDLE CONSECUTIVE CLASSES SPECIAL TO ACCELERATE
    low = 0
    high = 0
    for i in cgm_list:
        if low == 0:
            low = i
        if high == 0:
            high = i
        elif high == i - 1:
            high = i
        else:
            parameters_segmaths = input_seg + " -thr " + str(low-1) + " -uthr " + str(high+1) + " -bin -mul 3 -add " + \
                                  output_seg + " " + output_seg
            malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)
            low = i
            high = i

    if low > 0:
        parameters_segmaths = input_seg + " -thr " + str(low-1) + " -uthr " + str(high+1) + " -bin -mul 3 -add " + \
                              output_seg + " " + output_seg
        malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)
# DONE CGM

    for i in wm_list:
        parameters_segmaths = input_seg + " -thr " + str(i-1) + " -uthr " + str(i+1) + " -bin -mul 4 -add " + \
                              output_seg + " " + output_seg
        malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    for i in other_list:
        parameters_segmaths = input_seg + " -thr " + str(i-1) + " -uthr " + str(i+1) + " -bin -mul 5 -add " + \
                              output_seg + " " + output_seg
        malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    malpem.mytools.ensure_file(output_seg, "")
    malpem.mytools.finished_task(start_time, task_name)
    return True


def create_tissue_maps(input_file, malpem_prob_dir, output_dir):
    # DEFINITIONS
    binary_segmaths = os.path.join(malpem.mytools.__malpem_path__, "lib", "niftyseg", "seg_maths")

    # NMM STRUCTURE IDs FOR RESPECTIVE TISSUE CLASSES
    vent_list = [1, 2, 21, 22, 23, 24]
    cgm_list = range(41, 139, 1)
    dgm_list = range(1, 41, 1)
    wm_list = [12, 13, 16, 17]
    other_list = [14, 15, 18, 33, 34]
    
    for i in wm_list:
        dgm_list.remove(i)
    for i in vent_list:
        dgm_list.remove(i)
    for i in other_list:
        dgm_list.remove(i)
    # END DEFINITIONS

    task_name = "creating tissue probability maps from structural segmentation maps"
    start_time = malpem.mytools.start_task(task_name)

    log_dir = os.path.join(output_dir, "log/")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "tissue-maps-" + malpem.mytools.nifty_basename(input_file) + ".log")

    tissue_dummy = os.path.join(malpem_prob_dir, "posteriors_0.nii.gz")
    tissue_bg = os.path.join(malpem_prob_dir, "tissueMap_background.nii.gz")
    tissue_vent = os.path.join(malpem_prob_dir, "tissueMap_ventricles.nii.gz")
    tissue_dgm = os.path.join(malpem_prob_dir, "tissueMap_dGM.nii.gz")
    tissue_cgm = os.path.join(malpem_prob_dir, "tissueMap_cGM.nii.gz")
    tissue_wm = os.path.join(malpem_prob_dir, "tissueMap_WM.nii.gz")
    tissue_other = os.path.join(malpem_prob_dir, "tissueMap_other.nii.gz")

    malpem.mytools.ensure_file(tissue_dummy, "")

    parameters_segmaths = tissue_dummy + " -mul 0 "
    for i in vent_list:
        cur_map = os.path.join(malpem_prob_dir, "posteriors_" + str(i) + ".nii.gz")
        malpem.mytools.ensure_file(cur_map, "")
        parameters_segmaths += " -add " + cur_map
    parameters_segmaths += " " + tissue_vent
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    parameters_segmaths = tissue_dummy + " -mul 0 "
    for i in dgm_list:
        cur_map = os.path.join(malpem_prob_dir, "posteriors_" + str(i) + ".nii.gz")
        malpem.mytools.ensure_file(cur_map, "")
        parameters_segmaths += " -add " + cur_map
    parameters_segmaths += " " + tissue_dgm
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    parameters_segmaths = tissue_dummy + " -mul 0 "
    for i in cgm_list:
        cur_map = os.path.join(malpem_prob_dir, "posteriors_" + str(i) + ".nii.gz")
        malpem.mytools.ensure_file(cur_map, "")
        parameters_segmaths += " -add " + cur_map
    parameters_segmaths += " " + tissue_cgm
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    parameters_segmaths = tissue_dummy + " -mul 0 "
    for i in wm_list:
        cur_map = os.path.join(malpem_prob_dir, "posteriors_" + str(i) + ".nii.gz")
        malpem.mytools.ensure_file(cur_map, "")
        parameters_segmaths += " -add " + cur_map
    parameters_segmaths += " " + tissue_wm
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    parameters_segmaths = tissue_dummy + " -mul 0 "
    for i in other_list:
        cur_map = os.path.join(malpem_prob_dir, "posteriors_" + str(i) + ".nii.gz")
        malpem.mytools.ensure_file(cur_map, "")
        parameters_segmaths += " -add " + cur_map
    parameters_segmaths += " " + tissue_other
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    parameters_segmaths = tissue_dummy + " -add 1 -bin -sub " + tissue_vent + " -sub " + tissue_dgm + \
                        " -sub " + tissue_cgm + " -sub " + tissue_wm + " -sub " + tissue_other + " " + tissue_bg
    malpem.mytools.execute_cmd(binary_segmaths, parameters_segmaths, logfile)

    malpem.mytools.finished_task(start_time, task_name)
    return True

# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory


import time
from subprocess import call
import os
import malpem.mytools

def sym_dof(dof_a, dof_b, dof_out, output_dir):
# DEFINITIONS
    binary_sym = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_pairwiseSymDOF")
# END DEFINITIONS
    malpem.mytools.ensure_file(dof_a, "")
    malpem.mytools.ensure_file(dof_b, "")

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "dofsym.log")

    parameters_sym_dof = dof_a + " " + dof_b + " " + dof_out
    malpem.mytools.execute_cmd(binary_sym, parameters_sym_dof, logfile)
    malpem.mytools.ensure_file(dof_out, "")

def average_dofs(dofs_list, index, dof_out, output_dir):
# DEFINITIONS
    binary_average = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_averageDOFs")
# END DEFINITIONS
    parameters = str((len(dofs_list[index])-1)) + " "
    for i in range(len(dofs_list[index])):
        if i == index:
            continue

        malpem.mytools.ensure_file(dofs_list[index][i], "")
        parameters += dofs_list[index][i] + " "

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "dofaverage.log")

    parameters_average_dofs = parameters + " " + dof_out
    malpem.mytools.execute_cmd(binary_average, parameters_average_dofs, logfile)
    malpem.mytools.ensure_file(dof_out, "")

def dof2mni(source, dof_out, transformation_model, output_dir):
# DEFINITIONS
    mni_template = os.path.join(malpem.mytools.__malpem_path__, "atlas", "mni", "icbm_avg_152_t1_tal_lin_masked_div10000.nii.gz")
    mni_init_dof = os.path.join(output_dir, "mni_init.dof.gz")
# END DEFINITIONS
    if os.path.isfile(mni_init_dof):
        print("Using initialisation for MNI alignment: %s" % mni_init_dof)
        register(mni_template, source, mni_init_dof, dof_out, transformation_model, output_dir)
    else:
        register(mni_template, source, "", dof_out, transformation_model, output_dir)


def dofinvert(dof_in, dof_out, output_dir):
# DEFINITIONS
    binary_dofinvert = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "dofinvert")
# END DEFINITIONS
    malpem.mytools.ensure_file(dof_in, "")

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "dofinvert.log")

    parameters_dofinvert = dof_in + " " + dof_out
    malpem.mytools.execute_cmd(binary_dofinvert, parameters_dofinvert, logfile)
    malpem.mytools.ensure_file(dof_out, "")


def dofcombine(dof_a, dof_b, dof_out, inv_a, inv_b, output_dir):
# DEFINITIONS
    binary_dofcombine = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "dofcombine")
# END DEFINITIONS
    malpem.mytools.ensure_file(dof_a, "")
    malpem.mytools.ensure_file(dof_b, "")

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "dofcombine.log")

    parameters_dofcombine = dof_a + " " + dof_b + " " + dof_out
    if inv_a:
        parameters_dofcombine += " -invert1"
    if inv_b:
        parameters_dofcombine += " -invert2"

    malpem.mytools.execute_cmd(binary_dofcombine, parameters_dofcombine, logfile)
    malpem.mytools.ensure_file(dof_out, "")


def register(target, source, dof_in, dof_out, transformation_model, output_dir):
# DEFINITIONS
    binary_ireg = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "ireg")
    config_ireg = os.path.join(malpem.mytools.__malpem_path__, "etc", "ireg.cfg")
# END DEFINITIONS

    task_name = "Registration (" + transformation_model + ")"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(target, "")
    malpem.mytools.ensure_file(source, "")

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)
    logfile = os.path.join(log_dir, "registration-" + malpem.mytools.nifty_basename(source) + "-" +
                           malpem.mytools.nifty_basename(target) + ".log")

    parameters_ireg = target + " " + source + " -parin " + config_ireg + " -dofout " + dof_out

    if transformation_model == "rigid":
        parameters_ireg += " -model Rigid"
    elif transformation_model == "affine":
        parameters_ireg += " -model Rigid+Affine"

    if not dof_in == "":
        parameters_ireg += " -dofin " + dof_in

    malpem.mytools.execute_cmd(binary_ireg, parameters_ireg, logfile)

    malpem.mytools.ensure_file(dof_out, "")
    malpem.mytools.finished_task(start_time, task_name)
    return True


def transform(target, source, output_file, dof_in, interpolation, output_dir):
# DEFINITIONS
    binary_transformation = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "transformation")
# END DEFINITIONS

    task_name = "Transformation"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.ensure_file(target, "")
    malpem.mytools.ensure_file(source, "")
    if not dof_in == "":
        malpem.mytools.ensure_file(dof_in, "")

    log_dir = os.path.join(output_dir, "log")
    malpem.mytools.check_ex_dir(log_dir)

    logfile = os.path.join(log_dir, "transformation-" + malpem.mytools.nifty_basename(source) + "-" +
                           malpem.mytools.nifty_basename(target) + ".log")

    par_interpolation = "-linear"
    if interpolation == "nn":
        par_interpolation = "-nn"
    elif interpolation == "bspline":
        par_interpolation = "-bspline"
    else:
        par_interpolation = "-linear"

    if not dof_in == "":
        parameters_transformation = source + " " + output_file + " -target " + target + " -dofin " + \
                                    dof_in + " " + par_interpolation + " -matchInputType"
    else:
        parameters_transformation = source + " " + output_file + " -target " + target + \
                                    " " + par_interpolation + " -matchInputType"

    malpem.mytools.execute_cmd(binary_transformation, parameters_transformation, logfile)
    malpem.mytools.ensure_file(output_file, "")

    malpem.mytools.finished_task(start_time, task_name)
    return True


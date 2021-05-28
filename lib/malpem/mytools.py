# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory


from subprocess import call
import os
import time

__malpem_debug__ = "0"
__malpem_path__ = "."


def nifty_basename(input_file):
    base = os.path.basename(input_file)
    ext = os.path.splitext(base)[1]
    base = os.path.splitext(base)[0]
    if ext == ".gz":
        base = os.path.splitext(base)[0]

    return base


def basename(input_file):
    base = os.path.basename(input_file)
    base = os.path.splitext(base)[0]
    return base


def check_ex_dir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def ensure_file(filename, message):
    if not os.path.isfile(filename):
        print "--- ERROR: File does not exist (" + filename + "): " + message + " ---"
        return exit(1)
    return True


def execute_cmd(cmd, parameters, logfile):
    if logfile == "":
        final_cmd = cmd + " " + parameters
    else:
        final_cmd = cmd + " " + parameters + " >> " + logfile + " 2>&1"
        f = open(logfile, 'w')
        f.write(final_cmd + "\n")
        f.close()

    call(final_cmd, shell=True)


def start_task(task):
    print("--- STARTED %s ---" % task)
    return time.time()


def finished_task(start_time, task):
    seconds = time.time() - start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print("--- FINISHED %s in %d:%02d:%02d ---" % (task, h, m, s))


def get_id_string(input_list):
    result_string = "["
    tmp_first = -1
    tmp_last = -1
    for i in input_list:
        if tmp_first == -1:
            tmp_first = i
            tmp_last = i
        elif i == tmp_last + 1:
            tmp_last = i
        else:
            if result_string != "[":
                result_string += ","
            if tmp_first == tmp_last:
                result_string += str(tmp_first)
            else:
                result_string += str(tmp_first) + "-" + str(tmp_last)
            tmp_first = i
            tmp_last = i

    if tmp_first != -1:
        if result_string != "[":
            result_string += ","
        if tmp_first == tmp_last:
            result_string += str(tmp_first)
        else:
            result_string += str(tmp_first) + "-" + str(tmp_last)

    result_string += "]"
    return result_string
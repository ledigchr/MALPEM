# Author: Christian Ledig
#         Imperial College London
#         August, 2015
#
#         see license file in project root directory


import os
import time
import shutil
from reportlab.pdfgen import canvas
import malpem.mytools


def take_screenshot(output_file, parameters):
# DEFINITIONS
    binary_display = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "display")
    png_na = os.path.join(malpem.mytools.__malpem_path__, "etc", "screenshotNA.png")
# END DEFINITIONS

    task_name = "Taking Screenshot"
    start_time = malpem.mytools.start_task(task_name)

    parameters += " -offscreen " + output_file
    malpem.mytools.execute_cmd(binary_display, parameters, "")

    if not os.path.isfile(output_file):
        print("WARNING: Couldn't create screenshot (" + output_file + "): perhaps offscreen rendering failed")
        shutil.copyfile(png_na, output_file)

    malpem.mytools.ensure_file(output_file, "")
    malpem.mytools.finished_task(start_time, task_name)


def calculate_volume(input_seg, output_file):
# DEFINITIONS
    binary_volumes = os.path.join(malpem.mytools.__malpem_path__, "lib", "irtk", "cl_compute_volume")
# END DEFINITIONS

    task_name = "Calculating volumes"
    start_time = malpem.mytools.start_task(task_name)

    malpem.mytools.execute_cmd(binary_volumes, input_seg + " > " + output_file, "")

    malpem.mytools.ensure_file(output_file, "")
    malpem.mytools.finished_task(start_time, task_name)


def create_report(input_file, input_mask, input_seg_malpem, output_report, output_dir):
# DEFINITIONS
    structure_names = os.path.join(malpem.mytools.__malpem_path__, "etc", "nmm_info.csv")
    structure_lut = os.path.join(malpem.mytools.__malpem_path__, "etc", "lut.csv")

    # PAPER SIZE
    left_start = 50
    top_start = 800
    right_stop = 550

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

    total_brain_string = "[1-138]"
    vent_string = malpem.mytools.get_id_string(vent_list)
    cgm_string = malpem.mytools.get_id_string(cgm_list)
    dgm_string = malpem.mytools.get_id_string(dgm_list)
    wm_string = malpem.mytools.get_id_string(wm_list)
    other_string = malpem.mytools.get_id_string(other_list)
# END DEFINITIONS

# CALCULATE STRUCTURAL VOLUMES
    report_dir = os.path.join(output_dir, "report")
    malpem.mytools.check_ex_dir(report_dir)
    malpem_volume_file = os.path.join(report_dir, malpem.mytools.basename(output_report) + "_MALPEM_raw.csv")
    malpem_report_file = os.path.join(report_dir, malpem.mytools.basename(output_report) + "_MALPEM_Report.csv")

    calculate_volume(input_seg_malpem, malpem_volume_file)

    f = open(structure_names)
    s_id = []
    s_short = []
    s_long = []
    s_side = []
    s_volumes = []
    for row in f:
        arr = row.split(',')
        s_id.append(arr[0])
        s_short.append(arr[1])
        s_long.append(arr[2])
        s_side.append(arr[3])
    f.close()

    f = open(malpem_volume_file)
    for row in f:
        arr = row.split(',')
    for i in range(len(arr)):
        s_volumes.append(arr[i].lstrip())
    f.close()

    total_brain_volume = 0
    cgm_volume = 0
    dgm_volume = 0
    vent_volume = 0
    wm_volume = 0
    other_volume = 0

    for i in range(1, 139, 1):
        if i in vent_list:
            vent_volume += float(s_volumes[i])
        if i in cgm_list:
            cgm_volume += float(s_volumes[i])
        if i in dgm_list:
            dgm_volume += float(s_volumes[i])
        if i in wm_list:
            wm_volume += float(s_volumes[i])
        if i in other_list:
            other_volume += float(s_volumes[i])

    total_brain_volume = other_volume + vent_volume + cgm_volume + dgm_volume + wm_volume
# END

# TAKE RELEVANT SCREENSHOTS
    screenshots_malpem = []
    screenshots_malpem.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_MALPEM_xy.png"))
    screenshots_malpem.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_MALPEM_xz.png"))
    screenshots_malpem.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_MALPEM_yz.png"))

    screenshots_mask = []
    screenshots_mask.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_mask_xy.png"))
    screenshots_mask.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_mask_xz.png"))
    screenshots_mask.append(os.path.join(report_dir, malpem.mytools.basename(output_report) + "_mask_yz.png"))

    take_screenshot(screenshots_malpem[0], input_file + " -seg " + input_seg_malpem + " -lut " + structure_lut + " -xy -res 2")
    take_screenshot(screenshots_malpem[1], input_file + " -seg " + input_seg_malpem + " -lut " + structure_lut + " -xz -res 2")
    take_screenshot(screenshots_malpem[2], input_file + " -seg " + input_seg_malpem + " -lut " + structure_lut + " -yz -res 2")

    take_screenshot(screenshots_mask[0], input_file + " " + input_mask + " -scontour -xy -res 2")
    take_screenshot(screenshots_mask[1], input_file + " " + input_mask + " -scontour -xz -res 2")
    take_screenshot(screenshots_mask[2], input_file + " " + input_mask + " -scontour -yz -res 2")
# END

# CREATE CSV FILES
    f = open(malpem_report_file, 'wb+')
    f.write("ID,Structure,Volume [ml]\n")
    f.write(total_brain_string + "," + "TotalBrain" + "," + str(total_brain_volume/1000) + "\n")
    f.write(vent_string + "," + "Ventricle" + "," + str(vent_volume/1000) + "\n")
    f.write(dgm_string + "," + "NonCortical" + "," + str(dgm_volume/1000) + "\n")
    f.write(cgm_string + "," + "Cortical" + "," + str(cgm_volume/1000) + "\n")
    f.write(wm_string + "," + "WhiteMatter" + "," + str(wm_volume/1000) + "\n")
    f.write(other_string + "," + "Other" + "," + str(other_volume/1000) + "\n")

    for i in range(0, 139, 1):
        f.write(str(i) + "," + str(s_short[i]) + "," + str(float(s_volumes[i])/1000) + "\n")
    f.close()
# END

## START CREATING ACTUAL REPORT
    c = canvas.Canvas(output_report)
    c.line(left_start, top_start, right_stop, top_start)
    c.drawString(left_start, top_start-10, "Report based on MALPEM pipeline")
    c.line(left_start, top_start-15, right_stop, top_start-15)
    c.drawString(left_start, top_start-30, "File: " + input_file)
    c.drawString(left_start, top_start-50, "Date/Time: " + time.strftime("%c"))

    c.drawString(left_start, top_start-80, "Volumetric Summary")
    c.drawString(left_start + 150, top_start-80, "[ml]")
    c.drawString(left_start + 230, top_start-80, "rel. to total")
    c.drawString(left_start + 310, top_start-80, "IDs")
    c.line(left_start, top_start-85, right_stop, top_start-85)

    c.drawString(left_start, top_start-100, "total brain volume: ")
    c.drawString(left_start + 150, top_start-100, str(total_brain_volume/1000))
    c.drawString(left_start + 230, top_start-100, str(round(100*total_brain_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-100, total_brain_string)

    c.drawString(left_start, top_start-120, "ventricle volume: ")
    c.drawString(left_start + 150, top_start-120, str(vent_volume/1000))
    c.drawString(left_start + 230, top_start-120, str(round(100*vent_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-120, vent_string)

    c.drawString(left_start, top_start-140, "noncortical GM volume: ")
    c.drawString(left_start + 150, top_start-140, str(dgm_volume/1000))
    c.drawString(left_start + 230, top_start-140, str(round(100*dgm_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-140, dgm_string)

    c.drawString(left_start, top_start-160, "cortical GM volume: ")
    c.drawString(left_start + 150, top_start-160, str(cgm_volume/1000))
    c.drawString(left_start + 230, top_start-160, str(round(100*cgm_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-160, cgm_string)

    c.drawString(left_start, top_start-180, "white matter volume: ")
    c.drawString(left_start + 150, top_start-180, str(wm_volume/1000))
    c.drawString(left_start + 230, top_start-180, str(round(100*wm_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-180, wm_string)

    c.drawString(left_start, top_start-200, "other volume: ")
    c.drawString(left_start + 150, top_start-200, str(other_volume/1000))
    c.drawString(left_start + 230, top_start-200, str(round(100*other_volume/total_brain_volume, 2)) + "%")
    c.drawString(left_start + 310, top_start-200, other_string)

    img_width = (right_stop-left_start-10)/3

    c.drawString(left_start, top_start-240, "brain extraction (pincram)")
    c.drawInlineImage(screenshots_mask[0], left_start, top_start-240-5-img_width, img_width, img_width)
    c.drawInlineImage(screenshots_mask[1], left_start+165, top_start-240-5-img_width, img_width, img_width)
    c.drawInlineImage(screenshots_mask[2], left_start+330, top_start-240-5-img_width, img_width, img_width)

    c.drawString(left_start, top_start-240-1*(20+img_width), "whole brain segmentation (MALPEM with "
                                                             "Neuromorphometrics atlas)")
    c.drawInlineImage(screenshots_malpem[0], left_start, top_start-240-1*(20+img_width)-5-img_width, img_width, img_width)
    c.drawInlineImage(screenshots_malpem[1], left_start+165, top_start-240-1*(20+img_width)-5-img_width, img_width, img_width)
    c.drawInlineImage(screenshots_malpem[2], left_start+330, top_start-240-1*(20+img_width)-5-img_width, img_width, img_width)

    c.showPage()
    cur_line = 0
    cur_col = 0

    for i in range(len(s_volumes)):
        if i == 0:
            c.drawString(left_start, top_start-10, "Neuromorphometrics Volumes [ml]")
            c.line(left_start, top_start-15, right_stop, top_start-15)
            cur_line = 2
            cur_col = 0

        if i == 139:
            c.showPage()

            c.line(left_start, top_start-15, right_stop, top_start-15)
            cur_line = 2
            cur_col = 0

        c.drawString(left_start + cur_col * 280, top_start-10-cur_line*10, "(" + s_id[i] + ") ")
        c.drawString(left_start + cur_col * 280 + 30, top_start-10-cur_line*10, str(float(s_volumes[i])/1000))
        c.drawString(left_start + cur_col * 280 + 90, top_start-10-cur_line*10, "(" + s_short[i] + ")")
        cur_line += 1

        if cur_line > 72:
            if cur_col >= 1:
                cur_col = 0
                c.showPage()
            else:
                cur_col += 1
            cur_line = 2

    cur_line = 0
    for i in range(139):
        if i == 0:
            c.showPage()
            c.drawString(left_start, top_start-10, "Dictionary of Neuromorphometrics Structure Names "
                                                   "(remapped IDs from original Atlas)")
            c.line(left_start, top_start-15, right_stop, top_start-15)
            cur_line += 2
            c.line(left_start, top_start-10-cur_line*10+10, right_stop, top_start-10-cur_line*10+10)
            c.drawString(left_start, top_start-10-cur_line*10, "Non-Cortical Structures")
            c.line(left_start, top_start-10-cur_line*10-5, right_stop, top_start-10-cur_line*10-5)
            cur_line += 2

        if i == 41:
            cur_line += 1
            c.line(left_start, top_start-10-cur_line*10+10, right_stop, top_start-10-cur_line*10+10)
            c.drawString(left_start, top_start-10-cur_line*10, "Cortical Structures")
            c.line(left_start, top_start-10-cur_line*10-5, right_stop, top_start-10-cur_line*10-5)
            cur_line += 2

        if i == 139:
            if cur_line > 0:
                c.showPage()
            cur_line = 0

        c.drawString(left_start, top_start-10-cur_line*10, s_id[i])
        c.drawString(left_start+30, top_start-10-cur_line*10, s_short[i])
        if i > 40:
            c.drawString(left_start+130, top_start-10-cur_line*10, s_long[i])

        cur_line += 1

        if cur_line > 72:
            c.showPage()
            cur_line = 0

    c.save()


Introduction
============

The MALPEM distribution package consists of software and data files needed to perform a robust bias correction, brain extraction, and brain segmentation of a magnetic resonance brain image into 138 cortical and subcortical structures.

It was developed by [Christian Ledig][homepage] in the [BioMedIA][biomedia] group at
Imperial College London, UK.

_Acknowledgement_: Thanks to all co-authors mentioned below who contributed to the development of the employed methodology. Special thanks to [Andreas Schuh][schuschu] for implementing the image registration and giving valuable advice on the distribution of this software package.

If you use any part of this software for your brain image analysis,
please cite the following papers:

**Framework and segmentation**

   C. Ledig, R. A. Heckemann, A. Hammers, J. C. Lopez, V. F. J. Newcombe, A. Makropoulos, 
   J. Loetjoenen, D. Menon and D. Rueckert,
   "Robust whole-brain segmentation: Application to traumatic brain injury",
   Medical Image Analysis, 21(1), pp. 40-58, 2015.

**Brain extraction**

   R. Heckemann, C. Ledig, K. R. Gray, P. Aljabar, D. Rueckert, J. V. Hajnal, and A. Hammers,
   "Brain extraction using label propagation and group agreement: pincram",
   PLoS ONE, 10(7), pp. e0129211, 2015.

[homepage]: http://www.christianledig.com
[biomedia]: http://biomedic.doc.ic.ac.uk
[schuschu]: http://andreasschuh.com


Installation
============

The MALPEM software was developed on a 64-bit Linux system (Ubuntu 14.04) and is at the
moment only available as binary distribution which was packaged using [CARE][care].
This enables the execution of the software on any Linux system within a [confined execution
environment][proot] identical to our development environment. Advantages are that the
programs run on any Linux system and cannot interfere with other files on your system.

In the future, the source code of all software components will be released which will
enable the build and native installation on any supported operating system, including
in particular also Windows and OS X.

[care]: http://reproducible.io
[proot]: http://proot.me


Installation on Linux
---------------------

The online installer is [available here][download]. The installer downloads
and extracts all required resources and executable files in the installation directory
of MALPEM. Note that in the current version, all of the available resources are required
for a successful brain segmentation workflow execution.

To install MALPEM with all its resources in your home directory,
run the following commands in a [Terminal][terminal] window:

    cd
    wget -O malpem_installer.tar http://www.christianledig.com/Material/MALPEM/malpem_installer.tar
    tar xf malpem_installer.tar
    ./malpem_installer/malpem-install

The installer will list for each additional resource the license terms under which this
resource is made available and whether you accept these terms to proceed with the download
and installation. This will install all required programs and data files in a directory specified by the user (e.g., ```~/malpem-1.2```).

**Note**: For a system wide installation, you might want to install MALPEM to e.g. ```/opt/malpem-1.2``` as a root user. To do this run ```sudo ./malpem_installer/malpem-install```. Please note that while all files can be owned by root the directory ```lib/care/rootfs/tmp``` needs to  be read/writable by the user running MALPEM.

**Known Problem:** If you encounter a proot error (signal 11), please check this [issue][issue2].

**Tip**: The MALPEM package can be relocated by simply moving the complete installation folder.

[terminal]: https://help.ubuntu.com/community/UsingTheTerminal
[download]: http://www.christianledig.com/Material/MALPEM/malpem_installer.tar
[issue2]:  https://github.com/ledigchr/MALPEM/issues/2


Installation on Windows and OS X
--------------------------------

For non-Linux operating systems, a [virtual machine][vbox] (VM) running [Ubuntu][ubuntu] 14.04
or a later version is recommended. A good tutorial for how to setup a VM on Mac OS can be found [here][vmosx].

**Important:** Make sure that the VM has enough memory (e.g. 8 GB) and disk space (e.g. 16 GB) allocated to run MALPEM.

**Known Problem:** If you encounter a proot error (signal 11), please check this [issue][issue2].

[vbox]:   https://www.virtualbox.org
[ubuntu]: http://www.ubuntu.com/download/desktop
[vmosx]:  http://www.simplehelp.net/2015/06/09/how-to-install-ubuntu-on-your-mac/
[issue2]:  https://github.com/ledigchr/MALPEM/issues/2


Workflow execution
==================

To execute the brain segmentation workflow for a given brain MR image (e.g., ```input.nii.gz```),
including the bias correction and brain extraction steps, run the following command in a
[Terminal][terminal] window after changing to the MALPEM installation directory:

    cd ~/malpem-1.2
    bin/malpem-proot -i input.nii.gz -o outputDir

**Note:** We currently only support the [NIfTI][nifti] image file format.

A help screen with all the available workflow options can be displayed using the following
command:

    bin/malpem-proot -h

**Tip:** By adding the directory of your MALPEM installation (e.g. ```$HOME/malpem-1.2/bin/``` or ```/opt/malpem-1.2/bin/```)
to your [PATH][pathenv] environment variable, the segmentation can be executed from any
directory by simply typing the command ```malpem-proot```.

[nifti]: http://nifti.nimh.nih.gov
[pathenv]: http://www.cyberciti.biz/faq/unix-linux-adding-path/


System requirements
-------------------

**OS and CPU**

- Using CARE and a (virtual) Linux system, MALPEM can be run on any 64-bit machine.

**Disk space**

- At least 10 GB of free disk space are recommended for the installation and execution of MALPEM.
- The MALPEM package including all brain atlases occupies approximately 1.5 GB of disk space.
- The size of the output directory depends on the resolution of the input image. 
  For an image of size 256x256x150 voxels, approximately 500 MB including the transformations
  for the atlas propagation are required (see -c option to clean up unnecessary files after MALPEM has finished).
- During the execution, MALPEM creates several temporary files especially for the brain extraction.
  These temporary files can exceed 5 GB, but will be removed after the workflow execution.

**Memory**

- It is suggested to have at least 8 GB of memory available (allocated to the virtual machine).
- The memory requirements depend on the resolution of the input image and might exceed 8 GB.


Runtime
-------

The processing of an image (256x256x150) takes around 1-2 hours using 8 cores of a standard
desktop machine (see -t option). If MALPEM is run on a single core this increases to 
around 10 hours.


The proot environment
-------

The execution of MALPEM within a confined [proot][proot] environment (cf. Installation),
requires the use of a wrapper script (```bin/malpem-proot```) which manages the input and
output files of the workflow. This is because the programs executed within this environment
can only access files stored underneath the ```lib/care/rootfs``` directory. The installer
script creates hard links inside the ```lib/care/rootfs``` directory tree to required
resources of the MALPEM installation as the final installation step. This makes the
installed resources available to the programs executed within this environment.
Other, user supplied, input files as well as the output files of the workflow are copied
by the MALPEM wrapper script to and from this environment to make this process transparent
to the caller.


Example execution
=================

To test whether MALPEM is setup correctly run

    bin/malpem-proot -i atlas/pincram/limages/full/m100.nii.gz -o outputDir -t 8

This test should finish in approximately 10 hours when executed on a single core or about 1-2 hours
on a multi-core system with 8 threads (-t 8). The output directory will contain a binary brain mask for the
test image as well as a whole brain segmentation of 138 structures.
The volumes of the segmented structures are summarized in a PDF report file named ```m100_Report.pdf```. This report can be
compared to [this online available example report][report] to ensure that the obtained results are
similar to our results and that the framework is installed correctly.
Please note that minor numerical differences are expected, but the volume measures should be quite similar. 
If you suspect a problem with the installation or workflow execution, please contact [Christian Ledig][contact].

[report]: http://www.christianledig.com/Material/MALPEM/m100_Report.pdf
[contact]: http://www.christianledig.com/contact.html

**Explanation of parameters:**

    -i atlas/pincram/limages/full/m100.nii.gz   segment one of the PINCRAM atlas images
    -o outputDir                                output the results to outputDir (this will be created)
    -t 8                                        parallelize using 8 threads (if your machine has less
                                                or more CPU cores you might want to change this).

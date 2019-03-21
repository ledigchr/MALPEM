#!/bin/bash

cdir=$(dirname "$0")
. $cdir/common
cdir=$(normalpath "$cdir")

pn=$(basename $0)

commandline="$pn $*"

# Check that binaries are available
curdir=`dirname $0`
export PATH=${curdir}/../:${curdir}/../irtk:${curdir}/../niftyseg:$PATH
export LD_LIBRARY_PATH=${curdir}/../../lib/:$LD_LIBRARY_PATH

which ireg >/dev/null || fatal "IRTK ireg binary not found -- please ensure IRTK is on \$PATH"
which seg_maths >/dev/null || fatal "Nifty Seg seg_maths binary not found -- please ensure Nifty Seg is on \$PATH"

# Parameter handling
usage () { 
echo
echo "pincram version 0.2 "
echo
echo "Copyright (C) 2012-2013 Rolf A. Heckemann "
echo "Web site: http://www.soundray.org/pincram "
echo 
echo "Usage: $0 <input> <options> <-result result.nii.gz> <-output temp_output_dir> [-atlas atlas_directory] \\ "
echo "                       [-levels {2..5}] [-par max_parallel_jobs] [-ref ref.nii.gz] "
echo 
echo "<input>     : T1-weighted magnetic resonance image in gzipped NIfTI format."
echo 
echo "-result     : Name of file to receive output, a binary brain label image."
echo 
echo "-tempbase   : Temporary working directory.  Ideally a locally mounted directory."
echo "              To store intermediate output for later access, see -output option."
echo 
echo "-output     : Directory to receive intermediate output.  If a non-existent location is given,"
echo "              intermediate files will be discarded.  If not specified, the intermediate files will"
echo "              be copied to the directory of the result file."
echo 
echo "-atlas      : Atlas directory."
echo "            : Has to contain limages/full/m{1..n}.nii.gz, lmasks/full/m{1..n}.nii.gz "
echo "            : limages/margin-d5/m{1..n}.nii.gz, lmasks/margin-d5/m{1..n}.nii.gz and mninorm/m{1..n}.dof.gz "
echo 
echo "-tpn        : Rigid transformation for positional normalization of the target image (optional)"
echo "            : An image is considered positionally normalized if the centre of gravity is in the grid centre and"
echo "            : the midsagittal plane coincides with the grid centre plane."
echo 
echo "-atlasn     : Maximum number of atlases to use.  By default, all available are used."
echo 
echo "-levels     : Integer, minimum 1, maximum 3. Indicates level of refinement required."
echo 
echo "-ref        : Reference label against which to log Jaccard overlap results."
echo 
echo "-par        : Number of jobs to run in parallel (shell level).  Please use with consideration."
echo 
fatal "Parameter error"
}

[ $# -lt 3 ] && usage

tgt=$(normalpath "$1") ; shift
test -e $tgt || fatal "No image found -- $t"

tpn="$cdir"/neutral.dof.gz
result=
probresult=
par=1
ref=none
exclude=0
atlasdir=$(normalpath "$cdir"/atlas)
atlasn=0
tdbase="$cdir"/temp
outdir=notspecified
while [ $# -gt 0 ]
do
    case "$1" in
	-tpn)               tpn=$(normalpath "$2"); shift;;
	-result)         result=$(normalpath "$2"); shift;;
	-probresult) probresult=$(normalpath "$2"); shift;;
	-atlas)        atlasdir=$(normalpath "$2"); shift;;
	-output)         outdir=$(normalpath "$2"); shift;;
	-tempbase)       tdbase=$(normalpath "$2"); shift;;
	-ref)               ref=$(normalpath "$2"); shift;;
	-atlasn)         atlasn="$2"; shift;;
	-levels)         levels="$2"; shift;;
	-excludeatlas)  exclude="$2"; shift;;
	-par)               par="$2"; shift;;
	-queue)           queue="$2"; shift;;
	--) shift; break;;
        -*)
            usage;;
	*)  break;;
    esac
    shift
done

[ -e "$tpn" ] || fatal "Target positional normalization does not exist"

[ -n "$result" ] || fatal "Result filename not set"

[ -e "$atlasdir" ] || "Atlas directory does not exist"

[ "$outdir" = notspecified ] && outdir=$(basedir "$result")

atlasmax=$(ls "$atlasdir"/lmasks/full/m*nii.gz | wc -l)
[[ "$atlasn" =~ ^[0-9]+$ ]] || atlasn=$atlasmax
[[ "$atlasn" -gt $atlasmax || "$atlasn" -eq 0 ]] && atlasn=$atlasmax

## Set levels to three unless set to 1 or 2 via -levels option
[[ "$levels" =~ ^[1-2]$ ]] || levels=3
maxlevel=$[$levels-1]

[[ "$exclude" =~ ^[0-9]+$ ]] || exclude=0

[[ "$par" =~ ^[0-9]+$ ]] || par=1

[[ $queue =~ ^[[:alpha:]]+$ ]] || queue=

echo "Extracting $tgt"
echo "Writing brain label to $result"

# Functions

cleartospawn() { 
    local jobcount=$(jobs -r | grep -c .)
    if [ $jobcount -lt $par ] ; then
        return 0
    fi
    return 1
}

reg () {
    local tgt="$1" ; shift
    local src="$1" ; shift
    local srctr="$1" ; shift
    local msk="$1" ; shift
    local masktr="$1"; shift
    local dofin="$1"; shift
    local dofout="$1"; shift
    local spn="$1"; shift
    local tpn="$1"; shift
    local level="$1"; shift
    local ltd
    ltd=$(mktemp -d "$PWD"/reg$level.XXXXXX)
    local job=j$level
    cd $ltd || fatal "Error: cannot cd to temp directory $ltd"
    case $level in 
	0 ) 
	    echo "dofcombine "$spn" "$tpn" pre.dof.gz -invert2 >>"$ltd/log" 2>&1" >>$job 
	    # swap tgt and source to exploit availability of the atlas mask
	    # this required to invert to pre.dof.gz	
	    #echo "dofinvert pre.dof.gz pre.dof.gz >> "$ltd/log" 2>&1" >> $job
	    #echo "ireg "$src" "$tgt" -mask $msk -model Rigid -dofin pre.dof.gz -dofout "$dofout" >>"$ltd/log" 2>&1" >>$job 
	    #echo "dofinvert $dofout $dofout >>"$ltd/log" 2>&1" >>$job
	    echo "ireg "$tgt" "$src" -model Rigid -dofin pre.dof.gz -dofout "$dofout" >>"$ltd/log" 2>&1" >>$job
	    ;;
	1 ) 
	    # same as for rigid reg
	    #echo "dofinvert $dofin $dofout >> "$ltd/log" 2>&1" >>$job
            # the below config file for affine ireg is not used intentionally
	    #echo "ireg "$tgt" "$src" -model Affine -dofin "$dofin" -dofout "$dofout" -par \"Padding value = 0\" >>"$ltd/log" 2>&1" >>$job
	    echo "ireg "$tgt" "$src" -model Affine -dofin "$dofin" -dofout "$dofout" >>"$ltd/log" 2>&1" >>$job
	  	#echo "ireg "$tgt" "$src" -dofin "$dofin" -dofout "$dofout" -parin "$cdir/lev$level.cfg" >>"$ltd/log" 2>&1" >>$job

	    #echo "dofinvert $dofout $dofout >> "$ltd/log" 2>&1" >>$job
	    ;;
	[2-4] )
	    echo "ireg "$tgt" "$src" -dofin "$dofin" -dofout "$dofout" -parin "$cdir/lev$level.cfg" -parout "$ltd/parout" >>"$ltd/log" 2>&1" >> $job
	    ;;
    esac
    echo "transformation "$msk" "$masktr" -linear -dofin "$dofout" -target "$tgt" >>"$ltd/log" 2>&1" >>$job
    echo "transformation "$src" "$srctr" -linear -dofin "$dofout" -target "$tgt" >>"$ltd/log" 2>&1" >>$job 
    if [ $par -eq 1 ] ; then
	. $job 
    else
	. $job &
    fi
    cd ..
    return 0
}

assess() {
    local glabels="$1"
    if [ -e ref.nii.gz ] ; then 
	transformation "$glabels" assess.nii.gz -target ref.nii.gz >>noisy.log 2>&1
	echo -e "$glabels:\t\t"$(labelStats ref.nii.gz assess.nii.gz -q | cut -d ',' -f 1)
    fi
    return 0
}

# Temporary working directory
test -e "$tdbase" || mkdir -p "$tdbase"
td=$(mktemp -d "$tdbase/$(basename $0)-c$exclude.XXXXXX") || fatal "Could not create temp dir in $tdbase"
trap 'if [ -e "$outdir" ] ; then mv "$td" "$outdir"/ ; else rm -rf "$td" ; fi' 0 1 15 
cd "$td" || fatal "Error: cannot cd to temp directory $td"

echo "$commandline" >commandline.log

# Target preparation
originalorigin=$(info "$tgt" | grep origin | cut -d ' ' -f 4-6)
headertool "$tgt" target-full.nii.gz -origin 0 0 0 
convert "$tgt" target-full.nii.gz -float
[ -e "$ref" ] && cp "$ref" ref.nii.gz

# Arrays
levelname[0]="rigid"
levelname[1]="affine"
levelname[2]="nonrigid"
levelname[3]="none"

dmaskdil[0]=3
dmaskdil[1]=3

# Reduce these if there is a strong penalty on underinclusion
thr[0]=56
thr[1]=60
thr[2]=40

# Initialize first loop
tgt="$PWD"/target-full.nii.gz
prevlevel=init
seq 1 $atlasn | grep -vw $exclude >selection-$prevlevel.csv
nselected=$(cat selection-$prevlevel.csv | wc -l)
usepercent=$(echo $nselected | awk '{ printf "%.0f", 100*(8/$1)^(1/3) } ')

for level in $(seq 0 $maxlevel) ; do
    thislevel=${levelname[$level]}
    thisthr=${thr[$level]}
# Registration
    echo "Level $thislevel"
    for srcindex in $(cat selection-$prevlevel.csv) ; do
	sourcenii=m$srcindex.nii.gz
	src="$atlasdir"/limages/full/$sourcenii
	[ $level -ge 2 ] && src="$atlasdir"/limages/margin-d5/$sourcenii
	srctr="$PWD"/srctr-$thislevel-s$srcindex.nii.gz
	msk="$atlasdir"/lmasks/full/$sourcenii
	masktr="$PWD"/masktr-$thislevel-s$srcindex.nii.gz
	dofin="$PWD"/reg-s$srcindex-$prevlevel.dof.gz 
	dofout="$PWD"/reg-s$srcindex-$thislevel.dof.gz
	spn="$atlasdir"/mninorm/m$srcindex.dof.gz
	reg "$tgt" "$src" "$srctr" "$msk" "$masktr" "$dofin" "$dofout" "$spn" "$tpn" $level
	echo -n .
	while true ; do cleartospawn && break ; sleep 8 ; done
    done
    echo
# Wait for registration results
    wait

# Generate reference for atlas selection (fused from all)
    set -- $(ls masktr-$thislevel-s*)
    thissize=$#
    set -- $(echo $@ | sed 's/ / -add /g')
    seg_maths $@ -div $thissize tmask-$thislevel-atlas.nii.gz
    seg_maths tmask-$thislevel-atlas.nii.gz -thr 0.$thisthr -bin tmask-$thislevel.nii.gz 
    dilation tmask-$thislevel.nii.gz tmask-$thislevel-wide.nii.gz -iterations 1 >>noisy.log 2>&1
    erosion tmask-$thislevel.nii.gz tmask-$thislevel-narrow.nii.gz -iterations 1 >>noisy.log 2>&1
    subtract tmask-$thislevel-wide.nii.gz tmask-$thislevel-narrow.nii.gz emargin-$thislevel.nii.gz >>noisy.log 2>&1
    dilation emargin-$thislevel.nii.gz emargin-$thislevel-dil.nii.gz -iterations 3 >>noisy.log 2>&1
    padding target-full.nii.gz emargin-$thislevel-dil.nii.gz emasked-$thislevel.nii.gz 0 0
    assess tmask-$thislevel.nii.gz
# Selection
    echo "Selecting"
    for srcindex in $(cat selection-init.csv) ; do
	srctr="$PWD"/srctr-$thislevel-s$srcindex.nii.gz
	if [ -e $srctr ] ; then
	    echo $(evaluation emasked-$thislevel.nii.gz $srctr -Tp 0 -mask emargin-$thislevel-dil.nii.gz -linear | grep NMI | cut -d ' ' -f 2 )",$srcindex"
	fi
    done | sort -rn | tee simm-$thislevel.csv | cut -d , -f 2 > ranking-$thislevel.csv
    nselected=$[$thissize*$usepercent/100]
    [ $nselected -lt 9 ] && nselected=7
    split -l $nselected ranking-$thislevel.csv
    mv xaa selection-$thislevel.csv
    [ -e xab ] && cat x?? > unselected-$thislevel.csv 
    echo "Selected $nselected at $thislevel"
# Build label from selection 
    set -- $(head -n 19 selection-$thislevel.csv | while read -r item ; do echo masktr-$thislevel-s$item.nii.gz ; done)
    thissize=$#
    set -- $(echo $@ | sed 's/ / -add /g')
    seg_maths $@ -div $thissize tmask-$thislevel-sel-atlas.nii.gz 
    seg_maths tmask-$thislevel-sel-atlas.nii.gz -thr 0.$thisthr -bin tmask-$thislevel-sel.nii.gz 
    assess tmask-$thislevel-sel.nii.gz
# Data mask (skip on last iteration)
    [ $level -eq $maxlevel ] && continue
    seg_maths tmask-$thislevel-sel-atlas.nii.gz -thr 0.15 -bin tmask-$thislevel-wide.nii.gz
    seg_maths tmask-$thislevel-sel-atlas.nii.gz -thr 0.99 -bin tmask-$thislevel-narrow.nii.gz
    subtract tmask-$thislevel-wide.nii.gz tmask-$thislevel-narrow.nii.gz dmargin-$thislevel.nii.gz -no_norm >>noisy.log 2>&1
    dilation dmargin-$thislevel.nii.gz dmargin-$thislevel-dil.nii.gz -iterations ${dmaskdil[$level]} >>noisy.log 2>&1
    padding target-full.nii.gz dmargin-$thislevel-dil.nii.gz dmasked-$thislevel.nii.gz 0 0
    tgt="$PWD"/dmasked-$thislevel.nii.gz
    prevlevel=$thislevel
done

convert tmask-$thislevel-sel.nii.gz output.nii.gz -short >>noisy.log 2>&1
headertool output.nii.gz "$result" -origin $originalorigin

exit 0

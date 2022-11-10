import argparse
import os.path as op
from fsub_extractor.utils.utils import *
from dipy.tracking.streamline import orient_by_rois
import dipy.stats.analysis as dsa
from dipy.io.image import load_nifti
from dipy.io.streamline import load_tractogram

# Add input arguments
def get_parser():

    parser = argparse.ArgumentParser(
        description="Extracts tract-average and along-the-tract measures of an input scalar metric (.nii.gz) along a specified streamline file (.tck/.trk)."
    )
    parser.add_argument(
        "--tract",
        help="Path to tract file (.tck or .trk). Should be in the same space as the scalar map inputs.",
        type=op.abspath,
        required=True,
    )
    parser.add_argument(
        "--scalars",
        help="Comma delimited list (no spaces) of path(s) to scalar maps (e.g. FA). This will also be used as a spatial reference file is a .trk file is passed in as a streamlines object.",
        required=True,
    )
    parser.add_argument(
        "--roi_begin",
        "--roi-begin",
        help="Binary ROI that will be used to denote where streamlines begin (lower number nodes on tract profiles)",
        type=op.abspath,
        required=True,
    )
    parser.add_argument(
        "--roi_end",
        "--roi-end",
        help="Binary ROI that will be used to denote where streamlines end (higher number nodes on tract profiles)",
        type=op.abspath,
        required=True,
    )
    parser.add_argument(
        "--nb_points",
        "--nb-points,
        help="Number of nodes to use in tract profile (default is 100)",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--out-dir",
        "--out_dir",
        help="Directory where outputs will be stored (a subject-folder will be created there if it does not exist).",
        type=op.abspath,
        default=os.getcwd(),
    )
    parser.add_argument(
        "--out-prefix",
        "--out_prefix",
        help="Prefix for all output files. Default is no prefix.",
        type=str,
        default="",
    )
    parser.add_argument(
        "--scratch",
        "--scratch",
        help="Path to scratch directory. Default is current directory.",
        type=op.abspath,
        default=os.getcwd(),
    )
    parser.add_argument(
        "--overwrite",
        help="Whether to overwrite outputs. Default is to overwrite.",
        default=True,
        action=argparse.BooleanOptionalAction,
    )

    return parser


def main():

    # Parse arguments and run the main code
    parser = get_parser()
    args = parser.parse_args()

    main = streamline_scalar(
        tract=args.tract,
        roi_begin=args.roi_begin,
        roi_end=args.roi_end,
        scalars=args.scalars,
        nb_points=args.nb_points,
        out_dir=args.out_dir,
        out_prefix=args.out_prefix,
        scratch=args.scratch,
        overwrite=args.overwrite,
    )


def streamline_scalar(
    tract,
    roi_begin,
    roi_end,
    scalars,
    nb_points,
    out_dir,
    out_prefix,
    scratch,
    overwrite,
):

    # TODO: add docs

    ### Split string of scalars in to list
    scalar_list = [op.abspath(scalar) for scalar in scalars.split(",")]
    for scalar in scalar_list:
        if op.exists(scalar) == False:
            raise Exception("Scalar map " + scalar + " not found on the system.")
            
    ### Check for assertion errors ###
    # Make sure tract file is okay
    if op.exists(tract) == False:
        raise Exception("Tract file " + tract + " is not found on the system.")
    if tract[-4:] not in [".trk", ".tck"]:
        raise Exception("Tract file " + tract + " is not of a supported file type.")
    # Use first scalar as reference file for trk streamlines
    if tract[-4:] == ".trk":
        trk_ref = scalar_list[0]
        print("\n Using " + trk_ref +" as reference image for TRK file. \n")
    # Convert .trk to .tck if needed
        print(" Converting .trk to .tck \n")
        tck_file = trk_to_tck(tract, trk_ref, out_dir, overwrite)
    else:
        tck_file = tract
    # Make sure number of points is not negative
    if nb_points < 2:
        raise Exception("Number of points must be an integer larger than 1.")
    # Check if out and scratch directories exist
    if op.isdir(out_dir) == False:
        raise Exception("Output directory " + out_dir + " not found on the system.")
    if op.isdir(scratch) == False:
        raise Exception("Scratch directory " + scratch + " not found on the system.")

    ### Prepare output directories ###
    # Add an underscore to separate prefix from file names if a prefix is specified
    if len(out_prefix) > 0:
        if out_prefix[-1] != "_":
            out_prefix += "_"

    # Make subject output and scratch folders if they do not exist, and define the naming convention
    if op.isdir(op.join(out_dir, subject)) == False:
        os.mkdir(op.join(out_dir, subject))
    if op.isdir(op.join(scratch, subject + "_scratch")) == False:
        os.mkdir(op.join(scratch, subject + "_scratch"))
    subject_base = op.join(out_dir,subject)
    outpath_base = op.join(subject_base, out_prefix)
    scratch_base = op.join(scratch, subject + "_scratch", out_prefix)

    ### Reorient streamlines so beginning of each streamline are at the same end
    bundle = load_tractogram(tck_file, trk_ref)
    trk_ref_img, ref_affine = load_nifti(trk_ref)
    oriented_bundle = orient_by_rois(
        tck_file,
        ref_affine,
        roi_begin,
        roi_end)

    print("\n DONE \n")

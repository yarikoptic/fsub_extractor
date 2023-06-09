import argparse
import os
import os.path as op
from fsub_extractor.functions.extractor import extractor

# Add input arguments
def get_parser():

    parser = argparse.ArgumentParser(
        description="Functionally segments a tract file based on intersections with prespecified ROI(s) in gray matter."
    )
    parser.add_argument(
        "--subject",
        help="Subject name. This must match the subject name in the FreeSurfer folder.",
        required=True,
        metavar=("sub-XXX"),
    )
    parser.add_argument(
        "--tract",
        help="Path to original tract file (.tck or .trk). Should be in DWI space.",
        type=op.abspath,
        required=True,
        metavar=("/PATH/TO/TRACT.trk|.tck"),
    )
    parser.add_argument(
        "--tract-name",
        "--tract_name",
        help="Label for tract used in file names. Should not contain spaces. E.g., 'LeftAF' or 'wholebrain'. Default is 'tract'.",
        default="tract",
    )
    parser.add_argument(
        "--roi1",
        help="First ROI file (.mgz, .label, .gii, or .nii.gz). File should be binary (1 in ROI, 0 elsewhere).",
        type=op.abspath,
        required=True,
        metavar=("/PATH/TO/ROI1.mgz|.label|.gii|.nii.gz"),
    )
    parser.add_argument(
        "--roi1-name",
        "--roi1_name",
        help="Label for ROI1 outputs. Default is roi1",
        default="roi1",
    )
    parser.add_argument(
        "--roi2",
        help="Second ROI file (.mgz, .label, .gii, or .nii.gz). If specified, program will find streamlines connecting ROI1 and ROI2. File should be binary (1 in ROI, 0 elsewhere).",
        type=op.abspath,
        metavar=("/PATH/TO/ROI2.mgz|.label|.gii|.nii.gz"),
    )
    parser.add_argument(
        "--roi2-name",
        "--roi2_name",
        help="Label for ROI2 outputs. Default is roi2",
        default="roi2",
    )
    parser.add_argument(
        "--fs-dir",
        "--fs_dir",
        help="Path to FreeSurfer subjects directory. It should have a folder in it with your subject name. Required unless --skip-roi-proj is specified.",
        type=op.abspath,
        metavar=("/PATH/TO/FreeSurfer/SUBJECTSDIR/"),
    )
    parser.add_argument(
        "--hemi",
        help="FreeSurfer hemisphere name(s) corresponding to locations of the ROIs, separated by a comma (no spaces) if different for two ROIs (e.g 'lh,rh'). Required unless --skip-roi-proj is specified.",
        choices=["lh", "rh", "lh,rh", "rh,lh"],
        metavar=("{lh|rh|lh,rh|rh,lh}"),
    )
    parser.add_argument(
        "--fs2dwi",
        help="Path to registration for mapping FreeSurfer-to-DWI space. Mutually exclusive with --dwi2fs.",
        type=op.abspath,
        metavar=("/PATH/TO/FS2DWI-REG.lta|.txt|.mat"),
    )
    parser.add_argument(
        "--dwi2fs",
        help="Path to registration for mapping DWI-to-FreeSurfer space. Mutually exclusive with --fs2dwi.",
        type=op.abspath,
        metavar=("/PATH/TO/DWI2FS-REG.lta|.txt|.mat"),
    )
    parser.add_argument(
        "--reg-type",
        "--reg_type",
        choices=["LTA", "ITK", "FSL"],
        help="Registration format. LTA is the default for FreeSurfer and is .lta, ITK comes from ITK and ANTS and is presumed to be a .txt, FSL comes from FSL and is .mat. If left blank, will try to infer from file extension. Only try defining this if inferring the registration type does not work and creates errors.",
    )
    # parser.add_argument(
    #    "--fs-license",
    #    "--fs-license",
    #    help="Path to FreeSurfer license.",
    #    type=op.abspath,
    # )  # TODO: MAKE REQUIRED LATER FOR CONTAINER?
    parser.add_argument(
        "--gmwmi",
        help="Path to GMWMI image (.nii.gz or .mif). If not specified or not found, it will be created from FreeSurfer inputs. Ignored if --skip-gmwmi-intersection is specified. Should be in DWI space.",
        type=op.abspath,
        metavar=("/PATH/TO/GMWMI.nii.gz|.mif"),
    )
    parser.add_argument(
        "--gmwmi-thresh",
        "--gmwmi_thresh",
        help="Threshold above which to binarize the GMWMI image. Default is 0.0",
        type=float,
        default=0.0,
        metavar=("THRESHOLD"),
    )
    parser.add_argument(
        "--search-dist",
        "--search_dist",
        help="Distance in mm to search from streamlines for ROIs (float). Default is 3.0 mm.",
        type=float,
        default=3.0,
        metavar=("DISTANCE"),
    )
    parser.add_argument(
        "--search-type",
        "--search_type",
        choices=["forward", "radial", "reverse"],
        help="Method of searching for streamlines. Default is forward.",
        type=str,
        default="forward",
    )
    parser.add_argument(
        "--projfrac-params",
        "--projfrac_params",
        help="Comma delimited list (no spaces) of projfrac parameters for mri_surf2vol / mri_label2vol. Provided as start,stop,delta. Default is --projfrac-params='-1,0,0.1'. Start must be negative to project into white matter.",
        default="-1,0,0.1",
        metavar=("START,STOP,DELTA"),
    )
    parser.add_argument(
        "--sift2-weights",
        "--sift2_weights",
        help="Path to SIFT2 weights file. If supplied, the sum of weights will be output with streamline extraction.",
        type=op.abspath,
        metavar=("/PATH/TO/SIFT2_WEIGHTS.csv"),
    )
    parser.add_argument(
        "--exclude-mask",
        "--exclude_mask",
        help="Path to exclusion mask (.nii.gz or .mif). If specified, streamlines that enter this mask will be discarded. Must be in DWI space.",
        type=op.abspath,
        metavar=("/PATH/TO/EXCLUDE_MASK.nii.gz|.mif"),
    )
    parser.add_argument(
        "--include-mask",
        "--include_mask",
        help="Path to inclusion mask (.nii.gz or .mif). If specified, streamlines must intersect with this mask to be included (e.g., a waypoint ROI). Must be in DWI space.",
        type=op.abspath,
        metavar=("/PATH/TO/INCLUDE_MASK.nii.gz|.mif"),
    )
    parser.add_argument(
        "--out-dir",
        "--out_dir",
        help="Directory where outputs will be stored (a subject-folder will be created there if it does not exist). Default is current directory.",
        type=op.abspath,
        default=os.getcwd(),
        metavar=("/PATH/TO/OUTDIR/"),
    )
    parser.add_argument(
        "--overwrite",
        help="Whether to overwrite outputs. Default is to overwrite.",
        default=True,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--skip-roi-projection",
        "--skip_roi_projection",
        help="Whether to skip projecting ROI into WM (not recommended unless ROI is already projected). Default is to not skip projection.",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--skip-gmwmi-intersection",
        "--skip_gmwmi_intersection",
        help="Whether to skip intersecting ROI with GMWMI (not recommended unless ROI is already intersected). Default is to not skip intersection.",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    # Visualization arguments
    viz_args = parser.add_argument_group("Options for Visualization")
    viz_args.add_argument(
        "--make-viz",
        "--make_viz",
        help="Whether to make the output figure. Default is to not produce the figure.",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    viz_args.add_argument(
        "--interactive-viz",
        "--interactive_viz",
        help="Whether to produce an interactive visualization. Default is not interactive.",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    viz_args.add_argument(
        "--img-viz",
        "--img-viz",
        help="Path to image to plot in visualization (.nii.gz). Should be in DWI space.",
        type=op.abspath,
        metavar=("/PATH/TO/BACKGROUND_IMG.nii.gz"),
    )
    viz_args.add_argument(
        "--orig-color",
        "--orig_color",
        help="Comma-delimited (no spaces) color spec for original bundle in visualization, as fractional R,G,B. Default is 0.8,0.8,0.",
        default="0.8,0.8,0",
        metavar=("R,G,B"),
    )
    viz_args.add_argument(
        "--fsub-color",
        "--fsub_color",
        help="Comma-delimited (no spaces) color spec for FSuB bundle in visualization, as fractional R,G,B. Default is 0.2,0.6,1.",
        default="0.2,0.6,1",
        metavar=("R,G,B"),
    )
    viz_args.add_argument(
        "--roi1-color",
        "--roi1_color",
        help="Comma-delimited (no spaces) color spec for ROI1 in visualization, as fractional R,G,B. Default is 0.2,1,1.",
        default="0.2,1,1",
        metavar=("R,G,B"),
    )
    viz_args.add_argument(
        "--roi2-color",
        "--roi2_color",
        help="Comma-delimited (no spaces) color spec for ROI2 in visualization, as fractional R,G,B. Default is 1,0.2,1.",
        default="1,0.2,1",
        metavar=("R,G,B"),
    )
    viz_args.add_argument(
        "--roi-opacity",
        "--roi_opacity",
        help="Opacity (0,1) for ROI(s) in visualization (float). Default is 0.7.",
        default=0.7,
        type=float,
        metavar=("OPACITY"),
    )
    viz_args.add_argument(
        "--fsub-linewidth",
        "--fsub_linewidth",
        help="Linewidth for extracted steamlines in visualization (float). Default is 3.0.",
        default=3.0,
        type=float,
        metavar=("LINEWIDTH"),
    )
    viz_args.add_argument(
        "--axial-offset",
        "--axial_offset",
        help="Float (-1,1) describing where to display axial slice. -1.0 is bottom, 1.0 is top. Default is 0.0.",
        type=float,
        default=0.0,
        metavar=("OFFSET"),
    )
    viz_args.add_argument(
        "--saggital-offset",
        "--saggital_offset",
        help="Float (-1,1) describing where to display saggital slice. -1.0 is left, 1.0 is right. Default is 0.0.",
        type=float,
        default=0.0,
        metavar=("OFFSET"),
    )
    viz_args.add_argument(
        "--camera-angle",
        "--camera_angle",
        choices=["saggital", "axial"],
        help="Camera angle for visualization. Default is 'saggital.'",
        default="saggital",
    )

    return parser


def main():

    # Parse arguments and run the main code
    parser = get_parser()
    args = parser.parse_args()

    main = extractor(
        subject=args.subject,
        tract=args.tract,
        tract_name=args.tract_name,
        roi1=args.roi1,
        roi1_name=args.roi1_name,
        roi2=args.roi2,
        roi2_name=args.roi2_name,
        fs_dir=args.fs_dir,
        hemi=args.hemi,
        fs2dwi=args.fs2dwi,
        dwi2fs=args.dwi2fs,
        reg_type=args.reg_type,
        # fs_license=args.fs_license,
        gmwmi=args.gmwmi,
        gmwmi_thresh=args.gmwmi_thresh,
        search_dist=str(args.search_dist),
        search_type=str(args.search_type),
        projfrac_params=args.projfrac_params,
        sift2_weights=args.sift2_weights,
        exclude_mask=args.exclude_mask,
        include_mask=args.include_mask,
        out_dir=args.out_dir,
        overwrite=args.overwrite,
        skip_roi_projection=args.skip_roi_projection,
        skip_gmwmi_intersection=args.skip_gmwmi_intersection,
        make_viz=args.make_viz,
        interactive_viz=args.interactive_viz,
        img_viz=args.img_viz,
        orig_color=args.orig_color,
        fsub_color=args.fsub_color,
        roi1_color=args.roi1_color,
        roi2_color=args.roi2_color,
        roi_opacity=args.roi_opacity,
        fsub_linewidth=args.fsub_linewidth,
        axial_offset=args.axial_offset,
        saggital_offset=args.saggital_offset,
        camera_angle=args.camera_angle,
    )

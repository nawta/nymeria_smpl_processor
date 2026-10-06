"""
Play smpl_data.npz (output of preprocess_mvnx_to_smpl.py) in aitviewer.

Requires `pip install aitviewer` and the SMPL model at <smplx_models>/smpl/SMPL_MALE.pkl (or SMPL_FEMALE.pkl,
SMPL_NEUTRAL.pkl), where <smplx_models> is the folder set in aitviewer's aitvconfig.yaml. The data is Y-up, which is
aitviewer's default, so no axis change is applied.

Usage:
    python tools/view_aitviewer.py path/to/smpl_data.npz
    python tools/view_aitviewer.py path/to/smpl_data.npz --fps 30 --gender neutral
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation


def load_sequence(npz_path: Path, target_fps: float):
    """Return root and body axis-angle poses, translations, and the frame step used."""
    data = np.load(npz_path)
    if "local_poses" not in data:
        raise SystemExit("local_poses is missing; rerun preprocess_mvnx_to_smpl.py without --no-use-articulate.")
    json_path = npz_path.with_suffix(".json")
    source_fps = json.loads(json_path.read_text())["metadata"]["frame_rate"] if json_path.exists() else 240

    local = data["local_poses"]                                      # (N, 24, 3, 3)
    step = max(1, round(source_fps / target_fps))
    local = local[::step]
    n = local.shape[0]
    aa = Rotation.from_matrix(local.reshape(-1, 3, 3)).as_rotvec().reshape(n, 24, 3)
    return aa[:, 0], aa[:, 1:].reshape(n, 69), data["root_positions"][::step], source_fps / step


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npz", type=Path, help="smpl_data.npz written by preprocess_mvnx_to_smpl.py")
    parser.add_argument("--fps", type=float, default=30,
                        help="target rate after subsampling; the actual rate is the source rate divided by a whole number (default: 30)")
    parser.add_argument("--gender", default="male", choices=["male", "female", "neutral"],
                        help="SMPL model to load (default: male, matching basicmodel_m.pkl)")
    args = parser.parse_args()

    poses_root, poses_body, trans, fps = load_sequence(args.npz, args.fps)
    print(f"{len(trans)} frames at {fps:g} fps")

    from aitviewer.models.smpl import SMPLLayer
    from aitviewer.renderables.smpl import SMPLSequence
    from aitviewer.viewer import Viewer

    import torch

    smpl_layer = SMPLLayer(model_type="smpl", gender=args.gender)
    # root_positions is the pelvis position, while SMPL's translation moves the template, whose rest
    # pelvis is not at the origin. Subtract the rest pelvis so the pelvis lands on root_positions.
    with torch.no_grad():
        betas = smpl_layer.bm.shapedirs.new_zeros((1, smpl_layer.bm.shapedirs.shape[-1]))  # model's device and dtype
        rest_pelvis = smpl_layer.bm(betas=betas).joints[0, 0].cpu().numpy()

    sequence = SMPLSequence(
        poses_body=poses_body,
        poses_root=poses_root,
        trans=trans - rest_pelvis,
        smpl_layer=smpl_layer,
    )
    viewer = Viewer()
    viewer.playback_fps = fps
    viewer.scene.add(sequence)
    viewer.run()


if __name__ == "__main__":
    main()

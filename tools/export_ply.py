"""
Export SMPL meshes from smpl_data.npz (output of preprocess_mvnx_to_smpl.py) as PLY files.

Uses the articulate copy in mvnx_to_smpl/core/articulate, so no extra body-model package is needed.
PLY face indices are 0-based (OBJ is the format that starts at 1).

Usage:
    python tools/export_ply.py path/to/smpl_data.npz --frames 0
    python tools/export_ply.py path/to/smpl_data.npz --frames 0:2400:240 --out-dir meshes
    python tools/export_ply.py path/to/smpl_data.npz --frames all
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "mvnx_to_smpl"))

import core.articulate as art  # noqa: E402
from core.paths import Paths  # noqa: E402


def parse_frames(spec: str, num_frames: int) -> list:
    """'all', a single index '10', or a slice 'start:stop[:step]'."""
    if spec == "all":
        return list(range(num_frames))
    if ":" in spec:
        parts = [int(p) if p else None for p in spec.split(":")]
        return list(range(num_frames))[slice(*parts)]
    index = int(spec)
    if not 0 <= index < num_frames:
        raise ValueError(f"frame {index} is outside 0..{num_frames - 1}")
    return [index]


def write_ply(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    """Write a binary little-endian PLY with 0-based face indices."""
    vertices = np.ascontiguousarray(vertices, dtype="<f4")
    face_records = np.empty(len(faces), dtype=[("n", "u1"), ("idx", "<i4", (3,))])
    face_records["n"] = 3
    face_records["idx"] = faces
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {len(vertices)}\n"
        "property float x\nproperty float y\nproperty float z\n"
        f"element face {len(faces)}\n"
        "property list uchar int vertex_indices\n"
        "end_header\n"
    )
    with open(path, "wb") as f:
        f.write(header.encode("ascii"))
        f.write(vertices.tobytes())
        f.write(face_records.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("npz", type=Path, help="smpl_data.npz written by preprocess_mvnx_to_smpl.py")
    parser.add_argument("--frames", default="0", help="'all', an index, or start:stop[:step] (default: 0)")
    parser.add_argument("--out-dir", type=Path, default=Path("smpl_ply"), help="output folder (default: smpl_ply)")
    parser.add_argument("--smpl-model", type=Path, default=Paths.SMPL_FILE, help="SMPL .pkl file (default: the README setup path)")
    parser.add_argument("--pose-blendshape", action="store_true", help="apply SMPL pose corrective blend shapes")
    args = parser.parse_args()

    if not args.smpl_model.exists():
        sys.exit(f"SMPL model not found: {args.smpl_model}\nSee 'Setup: SMPL model' in README.md.")

    data = np.load(args.npz)
    if "local_poses" not in data:
        sys.exit("local_poses is missing; rerun preprocess_mvnx_to_smpl.py without --no-use-articulate.")
    local_poses = torch.from_numpy(data["local_poses"]).float()      # (N, 24, 3, 3)
    root_positions = torch.from_numpy(data["root_positions"]).float()  # (N, 3), pelvis position

    model = art.model.ParametricModel(str(args.smpl_model), use_pose_blendshape=args.pose_blendshape)
    faces = np.asarray(model.face, dtype=np.int64)

    frames = parse_frames(args.frames, local_poses.shape[0])
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for frame in frames:
        # articulate places the root joint at the origin, so adding the pelvis position puts the body in place.
        _, _, vertices = model.forward_kinematics(
            local_poses[frame:frame + 1], tran=root_positions[frame:frame + 1], calc_mesh=True
        )
        write_ply(args.out_dir / f"frame_{frame:06d}.ply", vertices[0].numpy(), faces)
    print(f"Wrote {len(frames)} PLY file(s) to {args.out_dir}")


if __name__ == "__main__":
    main()

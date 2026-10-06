# Nymeria SMPL Preprocessor

A script to convert MVNX motion capture data to SMPL format.



https://github.com/user-attachments/assets/ae70d5f8-799c-49a3-a74b-6ec6b94cf67b



## Overview

Converts MVNX files from the Nymeria dataset's `data_xdata_mvnx` directory to SMPL parameters and saves them to `data_smpl_from_xdata_mvnx`.

## Directory Structure

```
nymeria_smpl_preprocessor/
├── preprocess_mvnx_to_smpl.py  # Main script
├── mvnx_to_smpl/               # Support library
│   └── core/
│       ├── articulate/         # SMPL body model utilities
│       └── paths.py            # Path configuration
└── README.md
```

## Setup: SMPL model

The SMPL body model is not included in this repository, because its license does not allow redistribution.

1. Register at https://smpl.is.tue.mpg.de/ and download "SMPL for Python".
2. Copy the male model file (`basicmodel_m_lbs_10_207_0_v1.1.0.pkl` in version 1.1.0) to `mvnx_to_smpl/assets/smpl/basicmodel_m.pkl`.

## Usage

```bash
# Default (with local pose computation, recommended)
python preprocess_mvnx_to_smpl.py

# Custom paths
python preprocess_mvnx_to_smpl.py \
    --input-dir /path/to/data_xdata_mvnx \
    --output-dir /path/to/data_smpl_from_xdata_mvnx

# Without local poses (not recommended)
python preprocess_mvnx_to_smpl.py --no-use-articulate
```

## Output Format

The following files are generated in each sequence directory:

- `smpl_data.npz`: Numeric arrays only (numpy 1.x/2.x compatible)
  - `global_poses`: Global rotation matrices (N, 24, 3, 3)
  - `local_poses`: Local rotation matrices (N, 24, 3, 3)
  - `root_positions`: Pelvis positions in meters (N, 3)

Poses and positions are in a Y-up frame. `local_poses[:, 0]` is the root orientation and `local_poses[:, 1:]` are the other 23 joints, each relative to its parent.

- `smpl_data.json`: Metadata
  - `joint_names`: List of joint names
  - `metadata`: Frame rate and other info
  - `num_frames`: Number of frames
  - `*_shape`: Shape of each array

## Viewing and exporting meshes

Two scripts in `tools/` turn `smpl_data.npz` into something you can look at. Both use the SMPL model from "Setup: SMPL model".

```bash
# Write PLY meshes (one file per frame) for Blender, MeshLab, etc.
python tools/export_ply.py path/to/smpl_data.npz --frames 0:2400:240 --out-dir meshes

# Play the sequence in aitviewer
python tools/view_aitviewer.py path/to/smpl_data.npz --fps 30
```

For aitviewer, `pip install aitviewer`, then copy the SMPL model to `<smplx_models>/smpl/SMPL_MALE.pkl`, where `<smplx_models>` is the folder named by `smplx_models` in aitviewer's config file (`aitvconfig.yaml` in your working directory, for example `smplx_models: /path/to/body_models`). `--fps` subsamples the source frame rate stored in `smpl_data.json`, so the actual rate is the source rate divided by a whole number; the script prints it.

`export_ply.py` accepts `--frames all`, a single index, or `start:stop:step`. Both scripts place the pelvis at `root_positions`.

If loading the SMPL file fails with `No module named 'chumpy'`, the file is from an older SMPL release that stores its arrays as chumpy objects. Installing `chumpy` fixes it; chumpy needs NumPy older than 1.24.

## NumPy Compatibility

The npz files contain only numeric arrays, with metadata stored separately in JSON.
This avoids pickle compatibility issues between numpy 1.x and 2.x.

## Dependencies

- Python 3.8+
- PyTorch
- NumPy (1.x or 2.x)
- tqdm

## Third-party code

`mvnx_to_smpl/core/articulate/` is a copy of [articulate](https://github.com/Xinyu-Yi/articulate) by Xinyu Yi. See [its NOTICE](mvnx_to_smpl/core/articulate/NOTICE.md).

## License

The code in this repository is released under [CC BY-NC 4.0](LICENSE), the same license as the [Nymeria dataset code](https://github.com/facebookresearch/nymeria_dataset). Non-commercial use only. The SMPL model and the copied `articulate` code keep their own terms (see above).

## Related Projects

- [AITViewer](https://github.com/eth-ait/aitviewer): SMPL Visualization tool
- [Nymeria Dataset](https://github.com/facebookresearch/nymeria_dataset): Motion capture data from Aria glasses + MVN suit

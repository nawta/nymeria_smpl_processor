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
  - `root_positions`: Root positions (N, 3)

- `smpl_data.json`: Metadata
  - `joint_names`: List of joint names
  - `metadata`: Frame rate and other info
  - `num_frames`: Number of frames
  - `*_shape`: Shape of each array

## NumPy Compatibility

The npz files contain only numeric arrays, with metadata stored separately in JSON.
This avoids pickle compatibility issues between numpy 1.x and 2.x.

## Dependencies

- Python 3.8+
- PyTorch
- NumPy (1.x or 2.x)
- tqdm

## Related Projects

- [AITViewer](https://github.com/eth-ait/aitviewer): SMPL Visualization tool
- [Nymeria Dataset](https://github.com/facebookresearch/nymeria_dataset): Motion capture data from Aria glasses + MVN suit

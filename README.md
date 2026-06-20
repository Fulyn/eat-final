# Embodied AI Assignment 4

Course group project: train a diffusion policy for Galbot to grasp a hammer with the right gripper and strike a block. The active implementation lives in `Assignment4/`; run all RoboTwin commands from that directory.

## What is tracked here

- `Assignment4/envs/beat_block_hammer.py`: task and simulation logic.
- `Assignment4/task_config/`: clean and randomized Galbot task settings.
- `Assignment4/script/`: simulation collection and evaluation entry points.
- `Assignment4/policy/DP/`: the required Diffusion Policy baseline, including data processing, training, and deployment.
- `Assignment4_delta/GALBOT_UPDATE.md`: June 18 update notes for Galbot calibration, camera configuration, and test distributions.
- `Assignment4_delta/task_config/`: current Galbot camera/task configs distributed with the delta package.

The other directories under `Assignment4/policy/` are RoboTwin platform baselines. They are retained for reference but are not the planned solution path for this assignment.

## Deliberately not tracked

Datasets, downloaded simulation assets, split archives, trained checkpoints, videos, logs, and local Python environments are ignored. They are too large and/or course-distributed resources.

## Required downloads on the GPU server

1. **RoboTwin assets.** From `Assignment4/`, run `bash script/_download_assets.sh` after the Python environment is ready. This downloads the standard RoboTwin object and embodiment assets.
2. **Latest course delta package.** Download `Assignment4_delta.zip` from the course site. Its full `assets/embodiments/galbot-one-golf/` must be installed under `Assignment4/assets/embodiments/`. Keep the update's camera and task-config files aligned with `Assignment4_delta/GALBOT_UPDATE.md`.
3. **Real robot demonstrations.** Download the supplied `real_data_100.zarr.tar` and the two `final_robotwin_keep100_right8.zarr.tar.gz.*.part` files. Store them in an ignored `datasets/` directory, not Git.

Plan for at least 150 GB of free space before downloading assets and generating randomized simulation data.

## Main path

1. Set up RoboTwin and verify a tiny simulation run.
2. Install the latest Galbot delta assets/configuration.
3. Process real and simulated data into the 8D, head-camera format.
4. Train `policy/DP`, evaluate in simulation, and save candidate checkpoints for real-robot testing.

See the detailed course specification in `Assignment4(1).pdf`.

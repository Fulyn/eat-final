# Galbot Simulation Update

This update adds the assets and configuration needed to run the Galbot One Golf embodiment in the RoboTwin `beat_block_hammer` task.

## What Changed

### 1. Galbot embodiment assets

The assignment package now includes the Galbot embodiment under:

```text
assets/embodiments/galbot-one-golf/
```

This directory contains:

- the RoboTwin Galbot URDF used by SAPIEN: `urdf/galbot_one_golf_robotwin.urdf`
- Galbot mesh assets referenced by the URDF
- cuRobo configuration files
- the Galbot embodiment configuration: `config.yml`
- robot-specific calibrated RoboTwin URDFs in:

```text
assets/embodiments/galbot-one-golf/urdf/calibrated_by_robot_robotwin_numeric_only/
```

The calibrated URDFs keep the same link names, joint names, joint types, parent-child topology, axes, and mesh files as `galbot_one_golf_robotwin.urdf`. They only change numeric joint origin values.

Calibrated URDFs of the robots we will use for testing:

```text
galbot_one_golf_robotwin_R001ABDD22AA0029.urdf
galbot_one_golf_robotwin_R001ABDD22AA0030.urdf
galbot_one_golf_robotwin_R001ABDD22AA0047.urdf
galbot_one_golf_robotwin_R001ABDD22AA0105.urdf
galbot_one_golf_robotwin_R001ABDD22AA0140.urdf
```

### 2. Galbot head-left camera model

A Galbot head-left camera entry was added to:

```text
task_config/_camera_config.yml
```

The new camera type is:

```yaml
GalbotHeadLeft:
  fovy: 37
  w: 320
  h: 240
  near: 0.1
  far: 100.0
  fx: 123.92123501390626
  fy: 124.09785864872501
  cx: 161.7986225414375
  cy: 118.71803481431876
  skew: 0.0
```

Both Galbot task configs now use this head camera type:

```yaml
camera:
  head_camera_type: GalbotHeadLeft
```

### 3. Head camera extrinsics

The head camera pose is configured in:

```text
assets/embodiments/galbot-one-golf/config.yml
```

Look for the `static_camera_list` entry named `head_camera`. Its fields are:

```yaml
position: [...]
forward: [...]
left: [...]
```

These values define the SAPIEN static camera pose used by RoboTwin. To change the head camera extrinsics, edit this `head_camera` entry.

Recommended calibration randomization ranges for synthetic data generation:

```text
fx/fy:        +/- 0.5 px
cx/cy:        +/- 5 px
rotation:     +/- 0.01 rad
translation:  +/- 0.0075 m  # 7.5 mm
```

### 4. Robot base pose

The Galbot base pose is configured in:

```text
assets/embodiments/galbot-one-golf/config.yml
```

Look for:

```yaml
robot_pose:
- [x, y, z, qw, qx, qy, qz]
```

This update sets the default base pose so that the chassis front edge is approximately 20 cm from the table and the chassis left edge is approximately 10 cm from the table left side.

When generating synthetic training data, do not keep the base and table geometry perfectly fixed. Apply small randomization to the Galbot base pose, the table position, and the table size. The default values above should be treated as the center of the distribution, not as a single deterministic setup.

### 5. Median leg, head, and left-arm defaults

The Galbot embodiment config includes median default joint values measured from the real data distribution, which will also be used in testing:

- `fixed_joint_targets`: median leg and head joint values
- `homestate[0]`: median left-arm joint values
- `homestate[1]`: default right-arm joint values

The robot-specific calibrated RoboTwin URDFs bake the median fixed leg/head state into the fixed joints while preserving the RoboTwin URDF structure.

## Selecting a URDF

The task configs support selecting which Galbot URDF to use through `embodiment_config_overrides.urdf_path`.

Default RoboTwin URDF:

```yaml
embodiment_config_overrides:
  urdf_path: ./urdf/galbot_one_golf_robotwin.urdf
```

Example: use the calibrated URDF for robot `R001ABDD22AA0140`:

```yaml
embodiment_config_overrides:
  urdf_path: ./urdf/calibrated_by_robot_robotwin_numeric_only/galbot_one_golf_robotwin_R001ABDD22AA0140.urdf
```

The path is relative to:

```text
assets/embodiments/galbot-one-golf/
```


## Object Initialization Ranges

The hammer should be placed approximately at the center of the table in the real setup. In practice, it should still receive a small amount of randomization so that policies do not overfit to a single exact hammer pose.

For the block, use different ranges for the real-data test setting and the simulation-data test setting:

- Part 2 / real-data test setting:
  - `x` range: `[0.05, 0.20]`
  - `y` range: `[0.05, 0.25]`

- Part 3 / simulation-data test setting:
  - `x` range: `[0.05, 0.25]`
  - `y` range: `[0.00, 0.30]`

The current simulation implementation uses the Part 3 range. 

## Updated Task Configs

The following task configs were updated:

```text
task_config/galbot_demo_clean.yml
task_config/galbot_demo_randomized.yml
```

Both configs now:

- use `GalbotHeadLeft` for the head camera
- expose `urdf_path` under `embodiment_config_overrides`
- keep passive gripper mimic target settings enabled

The randomized config has background and clutter disabled by default because the full background and clutter assets are not included in this assignment package.

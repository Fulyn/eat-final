"""Merge compatible Diffusion Policy zarr datasets episode-by-episode.

This is intended for sim-to-real co-training: each source must contain
``data`` arrays with the same names/shapes and ``meta/episode_ends``.
The resulting episode boundaries are shifted so no trajectory crosses from
one source dataset into another.
"""

import argparse
import shutil
from pathlib import Path

import numpy as np
import zarr


def validate_source(root: zarr.Group, path: Path) -> tuple[list[str], int]:
    if "data" not in root or "meta" not in root or "episode_ends" not in root["meta"]:
        raise ValueError(f"{path} is not a Diffusion Policy zarr dataset")
    keys = sorted(root["data"].keys())
    if not keys:
        raise ValueError(f"{path} has no data arrays")
    ends = np.asarray(root["meta"]["episode_ends"][:], dtype=np.int64)
    if ends.ndim != 1 or len(ends) == 0 or np.any(np.diff(ends) <= 0):
        raise ValueError(f"{path} has invalid episode_ends")
    length = int(ends[-1])
    for key in keys:
        if root["data"][key].shape[0] != length:
            raise ValueError(f"{path}: data/{key} length disagrees with episode_ends")
    return keys, length


def copy_array(source: zarr.Array, destination: zarr.Array, offset: int) -> None:
    chunk = max(1, source.chunks[0])
    for start in range(0, source.shape[0], chunk):
        stop = min(start + chunk, source.shape[0])
        destination[offset + start : offset + stop] = source[start:stop]


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge compatible DP zarr datasets.")
    parser.add_argument("sources", nargs="+", type=Path, help="Input zarr directories, in sampling order")
    parser.add_argument("--output", required=True, type=Path, help="Output zarr directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory")
    args = parser.parse_args()

    if args.output.exists():
        if not args.overwrite:
            raise FileExistsError(f"{args.output} exists; pass --overwrite to replace it")
        shutil.rmtree(args.output)

    roots = [(path, zarr.open(str(path), mode="r")) for path in args.sources]
    reference_keys, _ = validate_source(roots[0][1], roots[0][0])
    reference = roots[0][1]["data"]
    source_info = []
    for path, root in roots:
        keys, length = validate_source(root, path)
        if keys != reference_keys:
            raise ValueError(f"{path}: data keys {keys} differ from {reference_keys}")
        for key in keys:
            array = root["data"][key]
            expected = reference[key]
            if array.shape[1:] != expected.shape[1:] or array.dtype != expected.dtype:
                raise ValueError(f"{path}: data/{key} is incompatible with the first source")
        source_info.append((path, root, length))

    total_steps = sum(length for _, _, length in source_info)
    total_episodes = sum(len(root["meta"]["episode_ends"]) for _, root, _ in source_info)
    compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=1)
    output = zarr.group(str(args.output))
    output_data = output.create_group("data")
    output_meta = output.create_group("meta")
    destination_arrays = {
        key: output_data.create_dataset(
            key,
            shape=(total_steps, *reference[key].shape[1:]),
            chunks=reference[key].chunks,
            dtype=reference[key].dtype,
            compressor=compressor,
        )
        for key in reference_keys
    }

    merged_ends = []
    offset = 0
    for path, root, length in source_info:
        print(f"copying {path} ({length} steps)")
        for key in reference_keys:
            copy_array(root["data"][key], destination_arrays[key], offset)
        merged_ends.extend((root["meta"]["episode_ends"][:] + offset).tolist())
        offset += length

    output_meta.create_dataset(
        "episode_ends",
        data=np.asarray(merged_ends, dtype=np.int64),
        chunks=(min(1024, total_episodes),),
        compressor=compressor,
    )
    print(f"wrote {args.output}: {total_episodes} episodes, {total_steps} steps")


if __name__ == "__main__":
    main()

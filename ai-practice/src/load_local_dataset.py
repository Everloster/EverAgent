"""Load an explicit Hugging Face dataset or local path without global cache scans."""

from __future__ import annotations

import argparse
from pathlib import Path


def load_and_show_dataset(
    dataset_name: str | None = None,
    local_path: str | Path | None = None,
    split: str = "train",
    num_samples: int = 10,
    trust_remote_code: bool = False,
):
    if bool(dataset_name) == bool(local_path):
        raise ValueError("provide exactly one of dataset_name or local_path")
    if num_samples < 0:
        raise ValueError("num_samples must be non-negative")
    from datasets import load_dataset, load_from_disk

    if dataset_name:
        dataset = load_dataset(
            dataset_name,
            split=split,
            trust_remote_code=trust_remote_code,
        )
    else:
        path = Path(local_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"dataset path does not exist: {path}")
        arrow_files = sorted(path.glob("*.arrow"))
        if arrow_files:
            dataset = load_dataset(
                "arrow", data_files=[str(file) for file in arrow_files], split=split
            )
        else:
            dataset = load_from_disk(str(path))
            if isinstance(dataset, dict):
                if split not in dataset:
                    raise ValueError(f"split {split!r} is not present in {path}")
                dataset = dataset[split]

    print(f"数据集大小: {len(dataset)} 条记录")
    print(f"数据集字段: {', '.join(dataset.column_names)}")
    for index in range(min(num_samples, len(dataset))):
        print(dataset[index])
    return dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dataset-name")
    source.add_argument("--local-path", type=Path)
    parser.add_argument("--split", default="train")
    parser.add_argument("--num-samples", type=int, default=10)
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="execute dataset-provided remote code only after reviewing that code",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_and_show_dataset(
        dataset_name=args.dataset_name,
        local_path=args.local_path,
        split=args.split,
        num_samples=args.num_samples,
        trust_remote_code=args.trust_remote_code,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

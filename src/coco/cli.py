"""Command-line interface for coco tool."""
from __future__ import annotations

import argparse
import os
import sys
import shutil
from typing import Optional

from coco.config import read_config
from coco.splitter import split_pdf


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="coco", description="Coco accounting PDF tools")
    sub = p.add_subparsers(dest="cmd")

    parser_split = sub.add_parser("split", help="Split PES PDF into components")
    # Make PES optional: if omitted, tool will try to find the PES in the project's resources
    parser_split.add_argument("pes", nargs="?", help="Path to PES PDF file to split (optional)")
    parser_split.add_argument("--out", help="Output folder (overrides config)")
    parser_split.add_argument(
        "--account-years",
        help="Accounting years like 2024-2025 (overrides config)",
    )

    return p


def _default_pes_path() -> str:
    # Location relative to package: project_root/resources/cc_2024-2025/EDD + FACTURES.pdf
    this = os.path.abspath(os.path.dirname(__file__))
    repo_root = os.path.abspath(os.path.join(this, "..", ".."))
    candidate = os.path.join(repo_root, "resources", "cc_2024-2025", "EDD + FACTURES.pdf")
    return candidate


def _deploy_resources_to_d_tmp(repo_root: Optional[str] = None) -> str:
    """Copy the project's resources/cc_2024-2025 into D:\\data\\tmp\cc_2024-2025.

    This creates the same folders structure as the manual setup: factures_a_controler (from a_controler),
    doublons, extra and the EDD + FACTURES.pdf file. Returns the path to the deployed PES PDF.
    """
    repo_root = repo_root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    src_dir = os.path.join(repo_root, "resources", "cc_2024-2025")
    dst_root = os.path.join("D:", "data", "tmp")
    dst_dir = os.path.join(dst_root, "cc_2024-2025")
    os.makedirs(dst_dir, exist_ok=True)

    # copy EDD + FACTURES.pdf
    src_pdf = os.path.join(src_dir, "EDD + FACTURES.pdf")
    if os.path.exists(src_pdf):
        shutil.copy2(src_pdf, dst_dir)

    # map and copy folders from resources/Factures
    factures_src = os.path.join(src_dir, "Factures")
    if os.path.exists(factures_src):
        # a_controler -> factures_a_controler
        a_ctrl = os.path.join(factures_src, "a_controler")
        if os.path.exists(a_ctrl):
            dst = os.path.join(dst_dir, "factures_a_controler")
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(a_ctrl, dst)

        # Doublons -> doublons
        doubl = os.path.join(factures_src, "Doublons")
        if os.path.exists(doubl):
            dst = os.path.join(dst_dir, "doublons")
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(doubl, dst)

        # extra -> extra
        extra = os.path.join(factures_src, "extra")
        if os.path.exists(extra):
            dst = os.path.join(dst_dir, "extra")
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(extra, dst)

    # copy user's .coco_cfg if present
    user_cfg = os.path.join(os.path.expanduser("~"), ".coco", ".coco_cfg")
    if os.path.exists(user_cfg):
        shutil.copy2(user_cfg, os.path.join(dst_root, ".coco_cfg"))

    return os.path.join(dst_dir, "EDD + FACTURES.pdf")


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    parser = build_parser()
    ns = parser.parse_args(argv)
    if not ns.cmd:
        parser.print_help()
        return 2

    cfg = read_config()
    if ns.cmd == "split":
        # Deploy resources into D:\data\tmp to match the manual layout requested.
        deployed_pes = _deploy_resources_to_d_tmp()
        pes = ns.pes or deployed_pes or _default_pes_path()
        if not os.path.exists(pes):
            print(f"PES file not found: {pes}")
            return 1
        # Force the output to be under D:\data\tmp\cc_2024-2025 so the user only runs `coco split`.
        out = ns.out or r"D:\data\tmp\cc_2024-2025"
        # ensure output directory exists
        os.makedirs(out, exist_ok=True)
        account_years = ns.account_years or cfg.account_years
        # account years format "YYYY-YYYY"
        end_year = account_years.split("-")[-1]
        res = split_pdf(pes, out, end_year)
        print("Split result:")
        for k, v in res.items():
            print(f"  {k}: {len(v)} items")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
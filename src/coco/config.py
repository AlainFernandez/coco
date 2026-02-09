"""Configuration helper for coco tool.

Reads .coco_cfg from user's home .coco directory or current directory.
Provides defaults for user.name, user.email, out.folder, account.years.
"""
from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from typing import Optional

DEFAULTS = {
    "user.name": "",
    "user.email": "",
    "out.folder": "",
    # account.years default computed dynamically
}

@dataclass
class CocoConfig:
    user_name: Optional[str]
    user_email: Optional[str]
    out_folder: str
    account_years: str


def _default_account_years() -> str:
    import datetime

    now = datetime.date.today()
    start = now.year
    end = start + 1
    return f"{start}-{end}"


def read_config(path: Optional[str] = None) -> CocoConfig:
    """Read configuration from given path or ~/.coco/.coco_cfg or ./ .coco_cfg.

    Precedence:
    - explicit path
    - $HOME/.coco/.coco_cfg
    - ./.coco_cfg
    - defaults
    """
    cfg = configparser.ConfigParser()
    paths_to_try = []
    if path:
        paths_to_try.append(path)
    home = os.path.expanduser("~")
    paths_to_try.append(os.path.join(home, ".coco", ".coco_cfg"))
    paths_to_try.append(os.path.join(os.getcwd(), ".coco_cfg"))

    found = None
    for p in paths_to_try:
        if os.path.exists(p):
            # Support simple key=value files without section headers by prepending [DEFAULT]
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    content = fh.read()
                if not content.strip():
                    cfg.read_string("")
                else:
                    # If file has no section header, add DEFAULT
                    if not any(line.strip().startswith("[") for line in content.splitlines()):
                        content = "[DEFAULT]\n" + content
                    cfg.read_string(content)
            except Exception:
                # fallback to normal read
                cfg.read(p)
            found = p
            break

    # values may be in DEFAULT section or root; support both
    def get(key: str) -> Optional[str]:
        if not found:
            return None
        if cfg.has_section("DEFAULT") and key in cfg["DEFAULT"]:
            return cfg["DEFAULT"].get(key)
        if key in cfg.defaults():
            return cfg.defaults().get(key)
        return None

    user_name = get("user.name")
    user_email = get("user.email")
    out_folder = get("out.folder") or ""
    account_years = get("account.years") or _default_account_years()

    # If out_folder is relative, expanduser and abspath
    if out_folder:
        out_folder = os.path.expanduser(out_folder)
        out_folder = os.path.abspath(out_folder)

    return CocoConfig(user_name, user_email, out_folder, account_years)

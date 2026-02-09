import os
import sys

# Ensure src is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from coco.config import read_config


def test_print_user_config():
    print("Testing config reading and printing:")
    cfg = read_config()
    if cfg is not None:
        print(f"user.name={cfg.user_name}")
        print(f"user.email={cfg.user_email}")
        print(f"out.folder={cfg.out_folder}")
        print(f"account.years={cfg.account_years}")
        # Ensure the config file was found or values defaulted
        # At minimum account.years should be set
        assert cfg.account_years is not None
    else:
        print("Could not read config")
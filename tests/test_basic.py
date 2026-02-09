from coco.config import read_config
from coco.cli import build_parser


def test_config_defaults():
    cfg = read_config(path=None)
    assert cfg.account_years is not None


def test_cli_parser():
    p = build_parser()
    assert p is not None

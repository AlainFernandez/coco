# coco
Management Assistant

## coco CLI

This repository now includes a minimal `coco` CLI under `src/coco` implementing the UReqs in `doc/spec/CH100_Account_Auditing.md`:

- `coco.config` reads `.coco_cfg` from `$HOME/.coco/.coco_cfg` or `./.coco_cfg` and provides defaults.
- `coco.splitter` implements a page-based PDF splitter using `pypdf`.
- `coco.cli` exposes a `split` subcommand: `python -m coco.cli split <pes.pdf>`.

See `requirements.txt` for dependencies.
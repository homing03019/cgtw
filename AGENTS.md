# AGENTS.md

## Cursor Cloud specific instructions

This repo is the **source/modding workspace** for the `cg2d` client of the MMORPG
魔力寶貝 / CrossGate. It is **not a single buildable app**. Keep these caveats in mind:

### What can and cannot run here (Linux cloud VM)

- **Cannot run on Linux:** the `cg2d.exe` game client and the `cgmsv` game server are
  Windows-only binaries that live **outside** this repo (gitignored — see `.gitignore`:
  `*.exe`, `bin/`, `data/`, `map/`). They also need a Locale Emulator (GBK) and a live
  network server. Do **not** attempt to launch them on the cloud VM; use `Start-CG2D.ps1`
  only on a Windows dev box.
- **Runnable/testable on Linux:** the Go asset toolchain in `tools/xgtool/`, plus the
  Python/PowerShell helper scripts (Python scripts use the standard library only).

### GBK encoding (critical)

- Files under `luaUI/` and `lua/` are **GBK-encoded**, not UTF-8 (see `.cursorrules` and
  `.cursor/rules/cgmsv-gbk-encoding.mdc`). Never edit Chinese strings with a plain
  UTF-8 editor apply; use Python `bytes` + GBK read/write.
- After editing any Lua with Chinese text, run:
  `python3 luaUI/scripts/verify_gbk.py <file>...` (exit 0 = OK). This is the primary
  "does my Lua still decode + render correctly" check on this VM.

### Go toolchain: `tools/xgtool` (the only real build target here)

- Standard commands (run from `tools/xgtool/`):
  - Build: `go build ./cmd/main.go`
  - Vet:   `go vet ./...`
  - Test:  `go test ./...`
  - Run:   `go run ./cmd/main.go <dump-graphic|dump-anime|convert-map> --help`
- Non-obvious: the `pkg/*_test.go` cases that need real game `*.bin` / `*.cgp` fixtures
  **skip automatically** because those files are gitignored (`tools/xgtool/.gitignore`).
  A green `go test ./...` with many SKIP lines under `xgtool/pkg` is expected and correct;
  the committed JSON fixtures under `internal/tmx/testdata/` do run for real.
- The `dump-*` / `convert-map` subcommands require external CrossGate `*.bin` game data,
  which is not in the repo, so they cannot do a real conversion here without that data.

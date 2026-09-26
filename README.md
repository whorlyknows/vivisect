# Vivisect — Complete Build Specification

> **Purpose**: This document is a self-contained, unambiguous build guide. It contains everything needed to implement the entire project from scratch — every file, every function, every integration point, with explicit code.

---

## 1. Project Overview

**Vivisect** is a CLI tool that attaches to any running Python process by PID and performs a comprehensive "autopsy" — collecting and displaying memory stats, threads, open files, network connections, environment variables, Python runtime info, and stack traces.

**Three output modes:**
1. **Rich terminal** (default) — colorful, formatted terminal output using the `rich` library
2. **JSON** (`--json`) — structured, machine-readable snapshot
3. **HTML** (`--html report.html`) — self-contained dark-themed dashboard

**Zero instrumentation** — the target process doesn't need any modifications. We use `psutil` for cross-platform process introspection.

## Quick install

```bash
pip install vivisect
```

## Features
- CPU & Memory Usage
- Threads enumeration
- Open Files
- Network Connections
- Python Runtime details
- Environment variables

## Usage

```bash
vivisect 12345
vivisect 12345 --json
vivisect 12345 --html out.html
vivisect --find gunicorn
```

## Platform support

| OS      | Supported |
|---------|-----------|
| Linux   | ✅        |
| macOS   | ✅        |
| Windows | ✅        |

## Contributing

Please open an issue on GitHub.

## License

MIT License.

## Why I built this

To easily diagnose issues in running python processes in staging/production without needing code modification.

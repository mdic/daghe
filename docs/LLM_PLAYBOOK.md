# DaGhE LLM PLAYBOOK

This document provides the mandatory operational standards and architectural invariants for Large Language Models (LLMs) working on the DaGhE (Distributed Automation & General Helper Engine) codebase.

---

## 1. Project Overview

DaGhE is a production-grade orchestration system for managing multiple Python and Bash automation jobs on a Linux VPS.

It provides:
- reliable job execution
- strict mutual exclusion
- reproducible environments
- unified observability

The system operates using a **Zero-Sudo model** via systemd user-instances and includes a Textual-based TUI for monitoring and maintenance.

---

## 2. System Architecture

All paths are relative to the project root (standardised at `/opt/daghe`).

- **`core/`**: Internal library. Contains logic for manifest parsing, state management, system interaction, and execution helpers.
- **`tui/`**: Textual application and `.tcss` styling.
- **`bin/`**: CLI entrypoints (`dgh`, `daghe`) and generated wrappers (`bin/generated/`).
- **`templates/`**: Blueprints for wrappers and systemd units.
- **`jobs/`**: Modules (`current/`) and their data (`data/`).
- **`state/`**: Lockfiles (`.lock`) and execution metadata (`.json`).
- **`logs/`**: Centralised logs per module.

---

## 2.1 Operational Commands (CLI)

Standard operational workflow:

- Install / regenerate module:
```bash
  uv run bin/dgh install <module-name>
````

* Run module:

  ```bash
  uv run bin/dgh run <module-name>
  ```

* Launch TUI:

  ```bash
  uv run bin/dgh tui
  ```

* Inspect logs:

  ```bash
  journalctl --user -u auto-<module-name>.service -n 50
  ```

### Notes

* `install` regenerates wrappers from templates.
* Modules must always be executed via wrappers.
* Direct Python execution is forbidden.

---

## 3. Execution Model (CRITICAL)

DaGhE uses a strict locking and process-replacement model.

### Wrapper Mechanism

1. Wrapper is launched via CLI or systemd
2. Opens FD 9 on `state/<name>.lock`
3. Acquires lock using `flock -n 9`
4. Executes payload using `exec`
5. Payload inherits lock
6. Lock is released only when payload terminates

### Running State Definition

* **Running**: lock is held
* **Idle**: lock is available

The lockfile is the **single source of truth**.

Never derive state from PIDs.

---

## 3.1 Responsibility Boundaries

* **Wrapper (`bin/generated/`)**

  * owns locking
  * executes payload
  * must remain minimal

* **Core (`core/`)**

  * business logic
  * manifest handling
  * state logic

* **CLI (`bin/dgh`)**

  * entrypoint
  * delegates to core
  * no duplicated logic

* **TUI (`tui/`)**

  * observes state
  * triggers actions
  * no business logic

---

## 4. Core Invariants (NON-NEGOTIABLE)

* Mutual exclusion must always hold
* Lock must span full execution
* No inline styling in Python
* No sudo usage
* State must be written atomically
* No silent failure fallback

---

## 4.1 Failure Model

Execution outcomes:

* success
* failure
* partial failure

Failures must:

* be written to `state/<module>.json`
* include:

  * exit code
  * timestamps (UTC)
  * summary

TUI must:

* reflect last outcome
* never assume success

Failures must never be ignored.

---

## 5. Coding Rules

* Minimal, local changes only
* UK English spelling
* Explicit error handling
* No environment leakage
* No duplication of logic

---

## 5.1 DO / DON'T Rules

### DO

* Use existing helpers in `core/`
* Probe lockfiles for running state
* Use TCSS for styling
* Validate manifests before actions

### DON'T

* Reimplement locking logic
* Use PID-based state detection
* Add inline styling in Python
* Use broad `except Exception`
* Bypass wrappers

---

## 6. TUI Rules (Textual)

* Styling only in `.tcss`
* Use semantic classes
* Use `@work(thread=True)` for long tasks
* Unified refresh logic required
* UI reflects real state only

---

## 7. Change Protocol (MANDATORY)

All changes must include:

1. Goal
2. Files modified
3. Exact code
4. Explanation
5. Verification

---

## 8. Allowed vs Forbidden Changes

### Allowed

* Bugfixes
* UI polish
* New core helpers
* New modules

### Forbidden

* Changing lock model
* Removing `exec`
* Breaking CLI
* Large redesigns
* Moving logic out of `core/`

---

## 9. Common Pitfalls

* FD inheritance errors
* Local-time timestamps
* Stale UI classes
* Path duplication
* Inline styling
* Broad exception handling

---

## 10. Testing Checklist

### Run

```bash
uv run bin/dgh run <module>
```

### Exclusion

Run twice → second must fail

### Kill test

```bash
pkill -f <module>
```

Expected:

* TUI → Idle
* new run allowed

### State

```bash
cat state/<module>.json
```

### TUI

* Sidebar indicator matches status panel
* Refresh updates correctly

---

## 11. Extension Guidelines

* New modules: `dgh newmod <name>`
* Extend TUI via widgets + TCSS
* Use core helpers, not duplication

---

## 12. Event Model (Future Extension)

Modules must emit structured events:

* level: debug/info/warning/error/success
* module name
* summary
* optional details

Notification system:

* consumes events
* applies templates
* renders output (e.g. Telegram)

Modules must NOT format notification messages.

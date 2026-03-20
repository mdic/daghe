# DaGhE LLM PLAYBOOK

This is a normative document. It defines the absolute architectural invariants and operational protocols for Large Language Models (LLMs) when modifying, extending, or maintaining the DaGhE (Distributed Automation & General Helper Engine) codebase.

---

## 1. Purpose
This playbook serves as the authoritative rulebook for AI assistants. It ensures that all code contributions remain consistent with established patterns, preserve critical safety mechanisms, and prevent architectural regressions.

---

## 2. Core Principles
*   **Orchestrator Centralisation**: The orchestrator (`bin/daghe` and `core/`) owns all control logic, environment preparation, and lifecycle management.
*   **Dumb Modules**: Individual modules must contain only task-specific logic. They must not manage their own scheduling, locking, or notification policies.
*   **State as Truth**: The system state is defined by the filesystem (locks and JSON state files). The UI and CLI must reflect this state, never speculate on it.
*   **State-First Notifications**: Notifications are a side-effect of a state change. State must be persisted to disk before any notification is dispatched.
*   **Minimalism**: Prefer small, explicit, and local changes over broad abstractions or speculative "future-proofing".
*   **No Implicit Redesign**: If a change requires altering an existing invariant, the LLM must stop and request explicit approval. Silent architectural changes are forbidden.

---

## 3. Execution Model
DaGhE uses a process-replacement model to ensure reliable locking.

*   **Wrapper Pattern**: Every job execution flows through a generated Bash wrapper (`bin/generated/run-<name>.sh`).
*   **flock Acquisition**: The wrapper opens File Descriptor 9 on `state/<name>.lock` and calls `flock -n 9`.
*   **exec Replacement**: If the lock is acquired, the wrapper uses the `exec` system call to launch the payload (e.g. `uv run python`).
*   **FD Inheritance**: Because `exec` is used, the payload process replaces the shell but **inherits** the open File Descriptor 9 and the associated lock.
*   **Liveness**: A module is "Running" if and only if the kernel-level lock on the `.lock` file is held.
*   **No Substitution**: The wrapper + `flock` + `exec` model must never be replaced with Python-based locking, PID tracking, or background daemons.
---

## 4. Locking Model
*   **Mutual Exclusion**: Only one instance of a module may run at any time.
*   **Kernel Integrity**: The system relies on the Linux kernel to release the `flock` automatically when the process (or its children) terminates. 
*   **Probing**: `is_module_running` in `core.state` must use a non-blocking `flock` probe to verify execution state. It must never rely solely on PID files or directory existence.
*   **No User-Space Locking**: Do not introduce lock files, PID files, or in-memory flags as alternatives to `flock`.

---

## 5. State & Notification Model
*   **Strict Sequencing**: All action paths must follow this order:
    1. Execute the task.
    2. Determine the outcome and exit code.
    3. Call `write_state(...)` to persist the result to `state/<name>.json`.
    4. Call `send_notification(...)` if the outcome requires it.
*   **Best-Effort Notifier**: The notifier is a non-critical utility. Failures in the notification layer must be logged but must **never** interrupt or crash the main execution flow.
*   **Confinement**: Notification triggers reside in the orchestrator actions, never inside the `core.state` library or module logic.
*   **Atomicity Requirement**: State writes must be atomic. Partial or corrupted state files are not acceptable.

---

## 6. Environment Model
*   **Venv Isolation**: All module subprocesses must use `core.system.get_clean_env()`.
*   **Leakage Prevention**: You must explicitly remove `VIRTUAL_ENV`, `PYTHONPATH`, and `__PYVENV_LAUNCHER__` from the environment before spawning a module process to avoid virtual environment nesting.
*   **Bus Discovery**: `systemctl --user` commands require the injection of `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS`. Use `get_user_bus_env()` for all system interactions.
*   **No Implicit Inheritance**: Subprocesses must not rely on ambient shell state. All required environment variables must be explicitly set.
* 
---

## 7. Orchestrator Rules
*   **`bin/daghe`**: This is the User Experience (UX) and Policy layer. It handles argument parsing, terminal output, and process-exit policies (`sys.exit`).
*   **`core/`**: This is the Mechanism layer. It must be stateless where possible, providing functional helpers that return data or subprocess results. It must not call `sys.exit()` or perform direct CLI logging.

---

## 8. TUI Rules (Textual)
*   **Threaded Workers**: All long-running operations (Sync, Upgrade, Run) must use the `@work(thread=True)` decorator.
*   **Non-Blocking UI**: The UI thread must remain responsive for navigation and selection at all times, even when a worker is active.
*   **TCSS Enforcement**: Zero visual styling is allowed in Python code. All colours, borders, and styles must be defined in `tui/styles.tcss` using semantic classes.
*   **Unified Refresh**: UI updates must trigger through a centralised refresh path (e.g. `action_refresh_all`) to ensure global consistency across panels.

---

## 9. Notifier Constraints
*   **Bash as Source**: `bin/telegram-notify.sh` is the single source of truth for the notification mechanism.
*   **Wrapper Role**: `core.notifier.py` is a thin subprocess wrapper. It must implement a safety timeout (default 10s) for every call.
*   **Stateless**: The notifier must not maintain a message queue or retry logic. It is a fire-and-forget helper.
*   **Optional Dependency**: The system must behave correctly even if the notifier is missing, misconfigured, or failing.

---

## 10. Change Protocol
When proposing changes, an LLM must:
1.  **Perform a Pre-flight Check**: Verify that the proposed change does not violate the `exec` model or the state/notification sequence.
2.  **Provide Minimal Diffs**: Deliver only the code necessary for the specific task.
3.  **Ensure Reversibility**: Changes must be additive or cleanly swappable.
4.  **UK English Standards**: Use UK English spelling for all strings, logs, and comments.
5.  **Stop on Uncertainty**: If the LLM is not certain about the impact of a change, it must stop and ask for clarification instead of guessing.

---

## 11. Explicit Anti-Patterns
*   **Bypassing Wrappers**: Never execute a module by calling Python directly from systemd; always use the generated wrapper.
*   **Silent Fallbacks**: Do not return a false "Success" or "Idle" state if a critical check (like manifest loading) fails.
*   **Inline Styling**: Do not use Textual's `[color]` or `[b]` markup for static UI elements.
*   **Duplication**: Do not re-implement discovery, pathing, or environment logic inside a module or new script; use `core`.
*   **Cross-Layer Leakage**: Do not introduce dependencies from `core` to orchestrator-level logic (e.g. notifier, CLI behaviour).
*   **State/Notify Inversion**: Never send notifications before writing state.

---

## 12. Definition of Done
A task is complete only when:
*   Invariants are preserved (Locking, Isolation, Naming).
*   Correctness is verified (Idle vs Running, Success vs Failure).
*   No regressions are introduced in existing modules.
*   UK English spelling is applied consistently.
*   All visual changes are confined to TCSS.
*   Notifications (if applicable) follow the defined level and wording conventions.

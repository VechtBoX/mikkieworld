# MIKKIE WORLD — BRAIN Architecture Design

## 1. Overview
The MIKKIE WORLD ecosystem consists of 27 specialized AI agents running locally on macOS. To ensure they work in harmony without conflicts, they are orchestrated by a central command system: the **BRAIN**.

## 2. Core Components

### 2.1 The Source of Truth: `BRAIN.md`
A simple Markdown file (`~/MIKKIE_WORLD/BRAIN.md`) where the user (Hendrik) writes ideas, campaigns, and instructions. This is the only file the user needs to edit.

### 2.2 The Orchestrator: `mikkie_brain.py`
A daemon that watches `BRAIN.md` for changes. When a change is detected, it parses the instructions, creates tasks, and delegates them to the appropriate specialized agents.

### 2.3 The Guardian: `mikkie_guardian.py`
A watchdog process that ensures all required agents are running. If an agent crashes, the Guardian restarts it and sends a Telegram alert.

### 2.4 The Heart: `mikkie_heart.py`
A validation agent that checks all generated content (text and images) against the MIKKIE WORLD brand values (Adventurous, Courageous, Magical) and safety guidelines (COPPA compliance, WWJD filter).

## 3. Communication Protocol

Agents communicate via a local JSON-based message queue system in `~/mikkieworld/queue/`.
- **Inbox:** Each agent has an inbox directory (e.g., `queue/artistly/`).
- **Messages:** Tasks are written as `.json` files into the inbox.
- **Processing:** The agent reads the JSON, performs the task, and moves the file to `queue/completed/` or `queue/failed/`.

## 4. Shared State
A central SQLite database or a robust JSON state file (`~/mikkieworld/mikkie_state.json`) maintains the global state, ensuring no duplicate work is done and providing a single source of truth for analytics.

## 5. Next Steps
1. Implement the queue system.
2. Build `mikkie_brain.py` to parse `BRAIN.md` and dispatch tasks.
3. Build `mikkie_heart.py` for content validation.
4. Build `mikkie_guardian.py` for process management.

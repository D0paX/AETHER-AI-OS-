# Aether OS: Documentation & Agent Rules

These rules define how the agent (Antigravity) must maintain the project's living documentation. They must be strictly followed upon the completion of any milestone or significant change.

## 1. Learning Journal (`docs/LEARNING_JOURNAL.md`)
- **Tone:** Plain English, beginner-friendly, heavily simplified.
- **Goal:** Explain *what* we did, *why* we did it, and *how* it works so the user maintains full, effortless knowledge of the AI OS. When logging changes or fixes, explicitly explain: what problem occurred, what problems it could cause in the future, and why we chose this specific solution to fix it.
- **Trigger:** Update this file whenever a milestone is completed, a complex concept is introduced, or a change/fix is made. Provide the "best explanation" possible.

## 2. Developer Diary (`docs/DEVELOPER_DIARY.md`)
- **Tone:** Principal Engineer / Lead Architect. Highly professional, technical, and mature.
- **Structure:**
  - **Group by Date:** Create a `### **Date:** YYYY-MM-DD` heading for each new day.
  - **Timestamps & Changes:** Log both Milestones AND arbitrary daily changes with exact timestamps (e.g., `2:21 PM - Completed M1.0`).
  - **End of Day Sign-off:** The very last line of any specific date's log must be exactly:
    `_(End of current log. Subsequent entries will be appended upon the completion of future milestones.)_`
  - **Updates:** When a new day starts, create a new Date block at the bottom of the document and repeat the process. Update this file whenever the user verifies that a change or milestone is complete.

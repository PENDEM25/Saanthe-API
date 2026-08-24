# Roles & Responsibilities
## Saanthe-API — Project Team Structure

*This document exists because a real SDLC always has named owners for each responsibility. Since this is a solo learning project, one person (Manoj) holds multiple hats, and Claude fills in as the rest of the team where practical. Documenting this explicitly avoids confusion later about "who decided what."*

---

### Team Roster

| Role | Held By | Core Responsibility in This Project |
|---|---|---|
| **Stakeholder / Business Owner** | Manoj | Approves scope, priorities, and final decisions. Has final say on all trade-offs. |
| **Product Manager (PM)** | Claude | Drafts formal artifacts (Charter, PRD, User Flows) based on stakeholder input. Facilitates structured discussion, doesn't unilaterally decide scope. |
| **Engineering Lead / Tech Lead** | Manoj | Owns technical feasibility calls, writes/approves architecture decisions, ultimately responsible for what gets built. |
| **Engineer (Implementer)** | Manoj | Writes and runs all code, hands-on, line by line. |
| **Technical Mentor / Architect (advisory)** | Claude | Proposes technical designs, explains trade-offs and concepts, reviews code and decisions — but does not write final code unsupervised or make unilateral architecture calls. |
| **QA / Test Engineer** | Manoj (with Claude drafting test plans/cases) | Executes and validates tests; Claude helps design what should be tested and why. |
| **DevOps** | Manoj (Claude advises on process) | Owns Git workflow, environment setup, eventual deployment steps. |

---

### Working Agreement (How Decisions Get Made)

1. **Claude never finalizes a scope, requirement, or design decision unilaterally.** Claude drafts a proposed version based on Manoj's stated input, and Manoj (as Stakeholder + Eng Lead) reviews, edits, or approves it.
2. **Manoj writes his POV first** for each phase/section before Claude drafts the formal document — this mirrors how a real PM gathers input from stakeholders before writing anything official.
3. **No phase is skipped**, but phases may be *combined* for efficiency (agreed earlier: condensed docs, but full hands-on execution).
4. **All formal artifacts live in `/docs`** in the GitHub repo, version-controlled like real engineering documentation — not just chat history.
5. **Claude does not write implementation code without Manoj running every step himself** — the goal is rebuild-capability, not a finished app.

---

### Why This Matters for Your Portfolio

Recruiters who look at your GitHub will not literally see "Claude" credited anywhere — this document is for *your* clarity during the build, and it's also a legitimate talking point in interviews: it shows you understand that real SDLC always has explicit ownership and review points, even when the "team" is small. You can honestly describe this project as one where you played PM, tech lead, and engineer simultaneously — a common reality at startups, and a positive signal, not a negative one.

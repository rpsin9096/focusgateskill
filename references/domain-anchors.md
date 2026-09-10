# Domain Anchors Reference

Grounding task vocabulary and architectural choices:

## 1. Domain Anchors (Micro-Glossary)
- Anchor task language using 1 to 5 canonical concepts.
- Define what each concept IS in 1–2 tight sentences.
- Designate forbidden synonyms under `_Replaces_`.

Example:
```markdown
- **SessionToken**: Cryptographically signed JWT stored in client cookies.
  _Replaces_: AuthKey, BearerId, AccessTicket
```

## 2. Decision Pins (Micro-ADRs)
Log inline architectural decisions when all three conditions hold:
1. Reversibility cost is high.
2. Surprising to an uninformed reader.
3. Selected from genuine competing alternatives.

Format:
```markdown
### [ADR-0001] In-Memory Ledger for Test Runs
- **Context & Trade-off**: Writing ledger to disk during tests added 2s; SQLite required native bindings.
- **Decision**: Use in-memory data store with file flush on exit.
```

## 3. System Promotion
Promote enduring terms and ADRs to root `CONTEXT.md` or `docs/adr/` upon task completion.

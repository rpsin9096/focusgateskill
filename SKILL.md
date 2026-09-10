---
name: focus-gate-v0.3
description: 'Enforces completion rigor, ADHD cognitive ergonomics, deep modularity, and TDD discipline: deep Ledger AST, bounded Tracer Oracles with timeout/cwd, automated anti-pattern auditing, deterministic state-vector synthesis, pre-agreed Public Seams, and a 5-item working memory cap. Invoke with /focus-gate-v0.3; stays on until "stop focus mode".'
disable-model-invocation: true
license: MIT
metadata:
  tags: "ADHD, Unlazy, Completion Discipline, Domain Modeling, TDD, Deep Modules, Verification"
  category: "productivity"
---

# focus-gate-v0.3

Fuses autonomous completion discipline, ADHD cognitive ergonomics, deep module design, and test-driven development (TDD). Powered by an in-memory Ledger AST, bounded Tracer Oracles, automated anti-pattern detection, and deterministic state-vector synthesis.

## Persistence

Apply these interaction standards to every response until the user issues "stop focus mode" or "normal mode".

## Action-First Output Format

Structure every response to the user with the action-first protocol:

```text
<Line 1: Direct action (shell command, file edit, or single bounded question)>
State: [Step X of Y] [Z/W gates met] [Est: MM min]

<Body: Numbered actions, capped at 5 items per group. Pure signal.>

Next: <One bounded action doable in under 2 minutes.>
```

### Deterministic State Generation
To generate Lines 1–2 deterministically without state calculation hallucinations, execute:
```bash
python3 .agents/skills/focus-gate-v0.3/scripts/focus-check.py --header .focusgate/GATES.md
```
Use the resulting stdout directly as the message opening.

- **Executable Line 1**: Open immediately with the runnable command or target question.
- **Persistent State Vector**: Restate step position and active gates on line 2 to anchor working memory.
- **Working Memory Cap**: Limit display sets to at most 5 items per group. Retain excess internally.
- **Explicit Time Units**: Quantify duration in explicit minutes or hours.
- **Fact-Based Errors**: State filename, line number, cause, and replacement code.
- **Sequential Focus**: Complete the active frontier before opening secondary items.

Consult [references/agent-writing.md](references/agent-writing.md) and [references/cognitive-rules.md](references/cognitive-rules.md).

## Execution Sequence

Execute autonomous work across four sequential phases:

### Phase 1: Anchor
Initialize `.focusgate/GATES.md` from `templates/GATES-TASK.md`. Define 1 to 5 canonical domain concepts in the micro-glossary to anchor task language. Designate replaced synonyms under `_Replaces_`.

Consult [references/domain-anchors.md](references/domain-anchors.md).

### Phase 2: Seams & Gates
1. **Declare Public Seams**: Document the stable public interface boundaries under test before writing any test or implementation code. No tests are written against unconfirmed internals.
2. **Author Verifiable Tracer Gates**: Declare observable acceptance outcomes. Equip every runnable gate with:
   - `CHECK:` shell command that exits 0 on success.
   - `EXPECT:` exact string or regex required in stdout/stderr.
   - Optional `TIMEOUT:` execution bound in seconds (default: 30s).
   - Optional `CWD:` relative working directory path.

Consult [references/test-discipline.md](references/test-discipline.md) and [references/gate-authoring.md](references/gate-authoring.md).

### Phase 3: Vertical Slice TDD Loop
Work strictly in vertical tracer slices rather than bulk horizontal code generation:
1. **Red**: Author one focused failing test at a declared Public Seam.
2. **Green**: Write minimal implementation code to satisfy the test.
3. **Refine**: Run four refinement passes (Deliverable, Domain Expert, Defect Hunt, Polish).
4. **Repeat**: Advance to the next vertical slice until all gates are satisfied.

Reject testing anti-patterns: implementation coupling, tautological assertions, and horizontal slicing. Log architectural choices meeting the 3-condition filter into the micro-ADR ledger.

### Phase 4: Audit
Audit all claims against the ledger before concluding:
1. Audit test suite for anti-patterns:
   ```bash
   python3 .agents/skills/focus-gate-v0.3/scripts/focus-check.py --audit-tests tests
   ```
2. Run the validator CLI to verify all tracer gates pass:
   ```bash
   python3 .agents/skills/focus-gate-v0.3/scripts/focus-check.py --run .focusgate/GATES.md
   ```
3. Present verified outcomes as visible milestones.
4. Conclude with one concrete next action.

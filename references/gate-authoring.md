# Gate Authoring Reference

Rules for creating verifiable tracer gates and executing refinement loops:

## 1. Tracer Gate Structure
Declare observable outcomes prior to code edits:
- Identifier and outcome title (`gate-1: <title>`).
- Indented `CHECK:` containing the exact shell command.
- Indented `EXPECT:` containing the expected token or regex.
- Optional indented `TIMEOUT:` bounded execution time in seconds (default: 30s).
- Optional indented `CWD:` relative working directory path.

```markdown
- [ ] gate-1: Server boots on port 8080
  CHECK: python3 -c "import server; print(server.PORT)"
  TIMEOUT: 10
  CWD: src
  EXPECT: 8080
```

## 2. Pass Criteria
Count a gate met when:
- Command exits 0 within the declared `TIMEOUT` bound.
- Combined output contains the exact `EXPECT:` token.

## 3. Four-Pass Refinement Loop
Apply four refinement passes to each deliverable:
1. **Deliverable Pass**: Build the complete, functional capability.
2. **Domain Expert Pass**: Replace basic logic with domain implementations aligned to anchors.
3. **Defect Hunt Pass**: Exercise boundary conditions, timeouts, and error handlers.
4. **Polish Pass**: Format code, tighten types, run `focus-check.py --audit-tests`, and confirm passing gates.

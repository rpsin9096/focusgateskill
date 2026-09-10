# Test Discipline Reference

Rigorous test-driven development (TDD) rules for autonomous agents:

## 1. Public Seams: Where Tests Live

A **Public Seam** is the stable public boundary of a module or component where external consumers observe behavior without reaching inside.

- **Pre-Agreed Seams**: Before authoring tests or implementation code, declare every seam under test in `.focusgate/GATES.md`.
- **Zero Internals**: Never target private functions, unexported helpers, or internal class states. Tests written at public seams survive internal refactoring without breaking.

## 2. Vertical Slices (Tracer Bullets)

Work strictly in vertical slices:
1. **Red**: Author one focused failing test targeting a declared public seam.
2. **Green**: Write minimal implementation code to satisfy the test. Run it to confirm it passes.
3. **Repeat**: Move to the next vertical slice.

Avoid horizontal bulk implementations where multiple components are coded before running tests.

## 3. Anti-Patterns Guardrails

Agents must actively reject three testing anti-patterns:

- **Implementation-coupled**: The test mocks internal private collaborators or verifies through side-channels. If refactoring internal code breaks the test while public behavior remains intact, the test is coupled.
- **Tautological**: The test assertion derives its expected outcome using the same logic as the code under test (e.g. `expect(add(a, b)).toBe(a + b)`). Expected values must originate from an independent specification or known-good literal.
- **Horizontal slicing**: Authoring all test cases upfront before implementing any logic, or writing all implementation code before writing tests. Bulk tests verify imagined interfaces rather than grounded behavior.

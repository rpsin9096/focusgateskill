# FocusGate Ledger: {Task Name}

State: [Step 1 of 4] [0/3 gates met] [Est: 20 min]

## 1. Domain Anchors (Micro-Glossary)

- **{CanonicalConcept}**: {1-2 tight sentences defining what it IS.}
  _Replaces_: {Synonym1, Synonym2}

---

## 2. Public Seams (Test Boundaries)

- **{SeamName}**: {Public function, module interface, or CLI contract under test}
  _Boundary_: {Public import or entrypoint path}

---

## 3. Acceptance Gates & Vertical Slices

- [ ] gate-1: {Observable outcome 1}
  CHECK: {shell command}
  EXPECT: {exact token}

- [ ] gate-2: {Observable outcome 2 with timeout}
  CHECK: {shell command}
  TIMEOUT: 15
  EXPECT: {exact token}

- [ ] gate-3: {Observable outcome 3 with custom working dir}
  CHECK: {shell command}
  CWD: {optional relative directory}
  EXPECT: {exact token}

---

## 4. Micro-ADR Ledger

- **[ADR-0001] Architecture Decision**: Accepted baseline configuration.

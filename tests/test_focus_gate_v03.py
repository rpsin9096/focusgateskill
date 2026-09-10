import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../.agents/skills/focus-gate-v0.3/scripts/focus-check.py")
)
MODULE_DIR = os.path.dirname(SCRIPT_PATH)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

class TestFocusGateV03(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        cmd = [sys.executable, SCRIPT_PATH] + list(args)
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    def test_ledger_ast_module_parsing(self):
        # Candidate 1: Deep Ledger module with clean domain AST
        import importlib.util
        spec = importlib.util.spec_from_file_location("focus_check", SCRIPT_PATH)
        fc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fc)
        self.assertTrue(hasattr(fc, "Ledger"), "Ledger class should be exported")

        content = """# FocusGate Ledger: Sample
State: [Step 1 of 3] [0/1 gates met] [Est: 10 min]

## 1. Domain Anchors (Micro-Glossary)
- **TokenA**: Definition of TokenA.

## 2. Public Seams (Test Boundaries)
- **InterfaceA**: Public interface A.

## 3. Acceptance Gates
- [ ] gate-1: First outcome
  CHECK: echo "hello"
  EXPECT: hello

## 4. Micro-ADR Ledger
- **[ADR-0001] Test**: Baseline ADR.
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name
        try:
            ledger = fc.Ledger.from_file(temp_path)
            self.assertEqual(len(ledger.glossary), 1)
            self.assertEqual(ledger.glossary[0]["term"], "TokenA")
            self.assertEqual(len(ledger.seams), 1)
            self.assertEqual(ledger.seams[0]["name"], "InterfaceA")
            self.assertEqual(len(ledger.gates), 1)
            self.assertEqual(ledger.gates[0]["id"], "gate-1")
            self.assertEqual(len(ledger.adrs), 1)
        finally:
            os.remove(temp_path)

    def test_state_vector_header_generation(self):
        # Candidate 2: State Vector Synthesizer CLI
        content = """# FocusGate Ledger: Demo
State: [Step 1 of 2] [0/2 gates met] [Est: 15 min]

## 1. Domain Anchors (Micro-Glossary)
- **TermA**: Def A

## 2. Public Seams (Test Boundaries)
- **SeamA**: Boundary A

## 3. Acceptance Gates
- [X] gate-1: First milestone
  CHECK: echo "1"
  EXPECT: 1
- [ ] gate-2: Second milestone
  CHECK: echo "2"
  EXPECT: 2
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name
        try:
            res = self.run_cli("--header", temp_path)
            self.assertEqual(res.returncode, 0)
            lines = res.stdout.strip().split("\n")
            self.assertTrue(len(lines) >= 2, "Expected at least 2 header lines")
            # Line 1 is the next action targeting gate-2
            self.assertIn("gate-2", lines[0])
            # Line 2 is the state vector: 1 of 2 gates met
            self.assertIn("State: [Step 2 of 2] [1/2 gates met]", lines[1])
        finally:
            os.remove(temp_path)

    def test_timeout_protection(self):
        # Candidate 3: Robust Tracer Oracle with TIMEOUT bound
        content = """# FocusGate Ledger
## 3. Acceptance Gates
- [ ] gate-slow: Command that hangs
  CHECK: python3 -c "import time; time.sleep(5)"
  TIMEOUT: 1
  EXPECT: done
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name
        try:
            res = self.run_cli("--run", temp_path)
            self.assertEqual(res.returncode, 1)
            self.assertIn("TIMEOUT", res.stdout)
        finally:
            os.remove(temp_path)

    def test_cwd_isolation(self):
        # Candidate 3: Tracer Oracle respecting CWD
        with tempfile.TemporaryDirectory() as temp_dir:
            sub_dir = os.path.join(temp_dir, "nested")
            os.makedirs(sub_dir, exist_ok=True)
            marker_file = os.path.join(sub_dir, "marker.txt")
            with open(marker_file, "w") as f:
                f.write("in-nested-dir")

            ledger_path = os.path.join(temp_dir, "GATES.md")
            content = f"""# FocusGate Ledger
## 3. Acceptance Gates
- [ ] gate-cwd: Read marker from nested cwd
  CHECK: python3 -c "print(open('marker.txt').read().strip())"
  CWD: nested
  EXPECT: in-nested-dir
"""
            with open(ledger_path, "w") as f:
                f.write(content)

            res = self.run_cli("--run", ledger_path, cwd=temp_dir)
            self.assertEqual(res.returncode, 0)
            self.assertIn("PASSED", res.stdout)

    def test_audit_tests_detects_anti_patterns(self):
        # Candidate 4: Automated Testing Anti-Pattern Linting
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_bad.py")
            # Build string dynamically so this test file itself doesn't contain the literal pattern
            private_call = "obj." + "_private" + "_helper()"
            taut_call = "self.assert" + "Equal(val, val)"
            with open(test_file, "w") as f:
                f.write(f"""import unittest
class BadTest(unittest.TestCase):
    def test_something(self):
        val = {private_call}
        {taut_call}
""")
            res = self.run_cli("--audit-tests", temp_dir)
            self.assertEqual(res.returncode, 1)
            self.assertIn("anti-pattern", res.stderr.lower())
            self.assertIn("_private_helper", res.stderr)
            self.assertIn("tautological", res.stderr.lower())

if __name__ == "__main__":
    unittest.main()

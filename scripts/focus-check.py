#!/usr/bin/env python3
import sys
import os
import re
import subprocess
from typing import List, Dict, Any, Tuple, Optional

class TracerGate:
    def __init__(self, gate_id: str, title: str, checked: bool = False, line_num: int = 0):
        self.id = gate_id
        self.title = title
        self.checked = checked
        self.line_num = line_num
        self.check_cmd: Optional[str] = None
        self.expect_pattern: Optional[str] = None
        self.timeout: int = 30
        self.cwd: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

class TracerOracle:
    @staticmethod
    def execute(gate: TracerGate, base_dir: str = ".") -> Tuple[bool, str]:
        if not gate.check_cmd:
            return True, f"[-] Skip {gate.id}: Manual gate"

        resolved_cwd = os.path.join(base_dir, gate.cwd) if gate.cwd else base_dir
        try:
            res = subprocess.run(
                gate.check_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=gate.timeout,
                cwd=resolved_cwd
            )
            output = res.stdout + res.stderr
            if res.returncode != 0:
                return False, f"FAILED (exit code {res.returncode})\n  {output.strip()}"
            if gate.expect_pattern and gate.expect_pattern not in output:
                return False, f"FAILED\n  Expected output to include: \"{gate.expect_pattern}\"\n  Received: \"{output.strip()}\""
            return True, "PASSED"
        except subprocess.TimeoutExpired:
            return False, f"TIMEOUT (exceeded {gate.timeout}s bound)"
        except Exception as e:
            return False, f"ERROR: {e}"

class Ledger:
    def __init__(self, content: str, filepath: str = ".focusgate/GATES.md"):
        self.filepath = filepath
        self.raw_content = content
        self.glossary: List[Dict[str, Any]] = []
        self.seams: List[Dict[str, Any]] = []
        self.gates: List[TracerGate] = []
        self.adrs: List[str] = []
        self.state_meta: Dict[str, Any] = {"step_total": 4, "step_current": 1, "est_min": 20}
        self._parse()

    @classmethod
    def from_file(cls, path: str) -> "Ledger":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Error: Ledger file not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return cls(f.read(), filepath=path)

    def _parse(self):
        lines = self.raw_content.split("\n")
        in_glossary = False
        in_seams = False
        in_adrs = False
        current_gate: Optional[TracerGate] = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            lower = line.lower()

            # Parse state line if present: State: [Step 1 of 4] [0/3 gates met] [Est: 20 min]
            state_m = re.search(r'state:\s*\[step\s*(\d+)\s*of\s*(\d+)\].*?\[est:\s*(\d+)\s*min\]', lower)
            if state_m:
                self.state_meta["step_current"] = int(state_m.group(1))
                self.state_meta["step_total"] = int(state_m.group(2))
                self.state_meta["est_min"] = int(state_m.group(3))

            if line.startswith("##") and ("micro-glossary" in lower or "domain anchor" in lower):
                in_glossary = True
                in_seams = False
                in_adrs = False
                continue
            if line.startswith("##") and ("public seam" in lower or "test boundar" in lower):
                in_glossary = False
                in_seams = True
                in_adrs = False
                continue
            if line.startswith("##") and ("acceptance gate" in lower or "vertical slice" in lower):
                in_glossary = False
                in_seams = False
                in_adrs = False
                continue
            if line.startswith("##") and ("micro-adr" in lower or "decision ledger" in lower):
                in_glossary = False
                in_seams = False
                in_adrs = True
                continue

            if in_glossary and stripped.startswith("- **"):
                m = re.match(r'- \*\*([^*]+)\*\*:\s*(.*)', stripped)
                if m:
                    self.glossary.append({"term": m.group(1).strip(), "def": m.group(2).strip(), "line": i + 1})

            if in_seams and stripped.startswith("- **"):
                m = re.match(r'- \*\*([^*]+)\*\*:\s*(.*)', stripped)
                if m:
                    self.seams.append({"name": m.group(1).strip(), "desc": m.group(2).strip(), "line": i + 1})

            gate_match = re.match(r'^-\s*\[([ xX])\]\s*([^:]+):\s*(.*)', stripped)
            if gate_match:
                current_gate = TracerGate(
                    gate_id=gate_match.group(2).strip(),
                    title=gate_match.group(3).strip(),
                    checked=gate_match.group(1).lower() == "x",
                    line_num=i + 1
                )
                self.gates.append(current_gate)
                continue

            if current_gate:
                chk_m = re.match(r'^\s*CHECK:\s*(.+)$', line)
                if chk_m:
                    current_gate.check_cmd = chk_m.group(1).strip()
                    continue
                exp_m = re.match(r'^\s*EXPECT:\s*(.+)$', line)
                if exp_m:
                    current_gate.expect_pattern = exp_m.group(1).strip()
                    continue
                to_m = re.match(r'^\s*TIMEOUT:\s*(\d+)$', line)
                if to_m:
                    current_gate.timeout = int(to_m.group(1).strip())
                    continue
                cwd_m = re.match(r'^\s*CWD:\s*(.+)$', line)
                if cwd_m:
                    current_gate.cwd = cwd_m.group(1).strip()
                    continue
                if stripped.startswith("- [") or line.startswith("## "):
                    current_gate = None

            if in_adrs and (stripped.startswith("### [ADR-") or stripped.startswith("- **[ADR-")):
                self.adrs.append(stripped)

    def lint(self, enforce_tdd: bool = False) -> Tuple[int, int, List[str], List[str]]:
        errors = 0
        warnings = 0
        logs = []
        err_logs = []

        logs.append(f"Linting FocusGate ledger: {self.filepath}\n")

        # 1. Glossary cap
        if len(self.glossary) > 5:
            err_logs.append(f"[ERROR] Glossary has {len(self.glossary)} terms. Maximum allowed is 5 to protect working memory.")
            errors += 1
        else:
            logs.append(f"[PASS] Glossary term count: {len(self.glossary)}/5")

        # 2. Public Seams (TDD check)
        if len(self.seams) > 0:
            logs.append(f"[PASS] Public Seams declared: {len(self.seams)}")
        else:
            if enforce_tdd:
                err_logs.append(f"[ERROR] Strict TDD requires at least one declared Public Seam before authoring gates.")
                errors += 1
            else:
                logs.append(f"[WARN] Ledger defines gates but no Public Seams are declared.")
                warnings += 1

        # 3. Gates exist
        if not self.gates:
            err_logs.append(f"[ERROR] No acceptance gates found.")
            errors += 1
        else:
            logs.append(f"[PASS] Found {len(self.gates)} gate definitions.")

        for g in self.gates:
            if not g.check_cmd:
                logs.append(f"[WARN] Gate '{g.id}' has no CHECK: command (manual gate).")
                warnings += 1
            if g.check_cmd and not g.expect_pattern:
                err_logs.append(f"[ERROR] Gate '{g.id}' has CHECK: but missing EXPECT: match pattern.")
                errors += 1

        # 4. ADHD 5-bullet block check
        blocks = self.raw_content.split("\n\n")
        for b in blocks:
            bullets = [l for l in b.split("\n") if l.strip().startswith("- ") or l.strip().startswith("* ")]
            if len(bullets) > 5:
                logs.append(f"[WARN] Block contains {len(bullets)} list items (> 5 items exceeds ADHD working memory limit).")
                warnings += 1

        return errors, warnings, logs, err_logs

    def status(self) -> str:
        met = sum(1 for g in self.gates if g.checked)
        total = len(self.gates)
        pct = round((met / total) * 100) if total else 0
        out = [
            f"FocusGate Status for {self.filepath}:",
            f"- Progress: {met}/{total} gates met ({pct}%)",
            f"- Terms anchored: {len(self.glossary)}",
            f"- Public seams: {len(self.seams)}",
            f"- ADRs recorded: {len(self.adrs)}\n",
            "Gates:"
        ]
        for g in self.gates:
            mark = "X" if g.checked else " "
            out.append(f"  [{mark}] {g.id}: {g.title}")
        return "\n".join(out)

    def run(self) -> Tuple[bool, List[str]]:
        base_dir = os.path.dirname(os.path.abspath(self.filepath))
        logs = [f"Executing runnable gates in {self.filepath}:\n"]
        all_passed = True

        for g in self.gates:
            if not g.check_cmd:
                logs.append(f"[-] Skip {g.id}: Manual gate")
                continue
            passed, msg = TracerOracle.execute(g, base_dir=base_dir)
            if passed:
                logs.append(f"Running {g.id} ({g.check_cmd})... {msg}")
            else:
                logs.append(f"Running {g.id} ({g.check_cmd})... {msg}")
                all_passed = False
        return all_passed, logs

    def state_vector(self) -> str:
        met = sum(1 for g in self.gates if g.checked)
        total = len(self.gates)
        # Identify first uncompleted gate
        uncompleted = next((g for g in self.gates if not g.checked), None)
        if uncompleted:
            line1 = f"Next action: {uncompleted.id} - {uncompleted.title}"
            step_current = min(met + 1, total)
        else:
            line1 = "All acceptance gates met. Audit complete."
            step_current = total

        line2 = f"State: [Step {step_current} of {total}] [{met}/{total} gates met] [Est: {self.state_meta['est_min']} min]"
        return f"{line1}\n{line2}"

    @staticmethod
    def audit_tests(target_path: str) -> Tuple[bool, List[str]]:
        errors = []
        files_to_check = []
        if os.path.isfile(target_path):
            files_to_check.append(target_path)
        elif os.path.isdir(target_path):
            for root, _, files in os.walk(target_path):
                for f in files:
                    if f.startswith("test_") and f.endswith(".py"):
                        files_to_check.append(os.path.join(root, f))

        for fpath in files_to_check:
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines):
                # Check for private member call coupling: obj._private_helper()
                m_private = re.search(r'\b[a-zA-Z0-9_]+\.(_[a-zA-Z0-9_]+)\(', line)
                if m_private:
                    errors.append(
                        f"[Anti-Pattern] Implementation-coupling in {fpath}:{idx+1}: "
                        f"calls private member '{m_private.group(1)}'. Test at public seams instead."
                    )
                # Check for tautological assertion: assertEqual(x, x)
                m_taut = re.search(r'assertEqual\(\s*([a-zA-Z0-9_]+)\s*,\s*\1\s*\)', line)
                if m_taut:
                    errors.append(
                        f"[Anti-Pattern] Tautological assertion in {fpath}:{idx+1}: "
                        f"asserts identical variable '{m_taut.group(1)}' against itself."
                    )

        return len(errors) == 0, errors

def print_help():
    print("""FocusGate Validator CLI v0.3
Usage:
  python3 focus-check.py --lint <path> [--enforce-tdd]    Validate ledger structure, cognitive rules, and public seams
  python3 focus-check.py --status <path>                 Display gates, glossary, seams, and ADR status
  python3 focus-check.py --run <path>                    Execute runnable gates with TIMEOUT and CWD support
  python3 focus-check.py --header <path>                 Emit Action Line 1 + ADHD State Vector Line 2
  python3 focus-check.py --audit-tests <dir_or_file>     Detect test anti-patterns (private coupling, tautologies)
""")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print_help()
        sys.exit(0)

    cmd = args[0]
    enforce_tdd = '--enforce-tdd' in args

    if cmd == '--audit-tests':
        target = args[1] if len(args) > 1 else 'tests'
        clean, issues = Ledger.audit_tests(target)
        if clean:
            print(f"[PASS] No testing anti-patterns detected in {target}.")
            sys.exit(0)
        else:
            print(f"[ERROR] Testing anti-patterns found in {target}:", file=sys.stderr)
            for issue in issues:
                print(f"  {issue}", file=sys.stderr)
            sys.exit(1)

    filepath = next((a for a in args[1:] if not a.startswith('--')), '.focusgate/GATES.md')

    try:
        ledger = Ledger.from_file(filepath)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if cmd == '--lint':
        errors, warnings, logs, err_logs = ledger.lint(enforce_tdd=enforce_tdd)
        for l in logs:
            print(l)
        for el in err_logs:
            print(el, file=sys.stderr)
        print(f"\nLint result: {errors} error(s), {warnings} warning(s).")
        sys.exit(1 if errors > 0 else 0)

    elif cmd == '--status':
        print(ledger.status())
        sys.exit(0)

    elif cmd == '--run':
        passed, logs = ledger.run()
        for l in logs:
            print(l)
        sys.exit(0 if passed else 1)

    elif cmd in ('--header', '--state-vector'):
        print(ledger.state_vector())
        sys.exit(0)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()

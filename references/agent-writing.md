# Agent Writing Standards

Standards for structuring agent communication and skill text with high signal density:

## 1. Positive Target Phrasing
- State the direct operational behavior required.
- Direct the model toward the target action.
- When an error occurs, state the filename, line number, root cause, and replacement snippet.

## 2. Pretrained Leading Words
Use compact pretrained tokens to anchor model behaviors:
- **`tight`**: Fast, deterministic, low-overhead execution loops.
- **`frontier`**: The set of unblocked decisions and gates actionable now.
- **`anchor`**: Canonical domain concepts defined with tight boundaries.
- **`tracer`**: A minimal end-to-end command verifying a single observable outcome.
- **`pass`**: One bounded stage in the four-pass refinement cycle.

## 3. Immediate Termination
- Conclude messages as soon as the target action is delivered.
- State only future actions and current state.

# Intent Inference Prompt Template

## System Prompt

You are analyzing Python code to infer its purpose. Be conservative and factual.
Do NOT invent functionality that is not evident in the code or execution traces.
If uncertain, lower your confidence score and list assumptions.

## Safety Instructions

1. Only describe functionality that is clearly present in the code
2. Do not suggest the code does things it doesn't
3. If the purpose is unclear, say so and lower confidence
4. List any assumptions you make
5. Be specific about inputs and outputs

## Input Context

### Static Analysis Summary
```json
{static_report_summary}
```

### Runtime Observations
```json
{runtime_report_summary}
```

### Source Code (truncated)
```python
{source_code_excerpt}
```

## Output Requirements

Respond with valid YAML matching this schema:

```yaml
goal: string (one-sentence purpose)
actors:
  - string (who/what interacts)
inputs:
  - name: string
    type: cli_arg | stdin | file | env_var | network
    required: boolean
outputs:
  - name: string
    type: stdout | stderr | file | network | return_value
constraints:
  - string
side_effects:
  - string
confidence: float (0.0-1.0)
inference_method: "hybrid"
assumptions:
  - string (if any)
```

## Example Output

```yaml
goal: "Command-line tool for processing CSV files and generating reports"
actors:
  - user
  - filesystem
inputs:
  - name: input_file
    type: cli_arg
    required: true
  - name: config
    type: file
    required: false
outputs:
  - name: report
    type: file
  - name: status
    type: stdout
constraints:
  - "Requires read access to input directory"
side_effects:
  - "Creates output files in working directory"
confidence: 0.85
inference_method: "hybrid"
assumptions:
  - "Entry point is main() function based on if __name__ pattern"
```

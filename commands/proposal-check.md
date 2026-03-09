# /proposal check

Display compliance matrix coverage status with breakdown by category.

## Usage

```
/proposal check
```

## Output

1. **Coverage breakdown** -- Items counted by status: covered, partial, missing, waived
2. **Waived distinction** -- Waived items shown separately from missing with explicit count
3. **Guidance** -- Actionable next steps when matrix is missing or malformed

## Examples

With a populated matrix:
```
47 items | 32 covered | 5 partial | 8 missing | 2 waived
```

Fresh matrix (all items not started):
```
47 items | 0 covered | 0 partial | 47 not started | 0 waived
```

No matrix found:
```
No compliance matrix found
Run the strategy wave command to generate a compliance matrix.
```

Malformed matrix file:
```
Could not parse compliance matrix
Verify the compliance matrix file format is valid markdown with the expected table structure.
```

## Implementation

This command invokes `ComplianceCheckService.check()` (driving port) which reads the compliance matrix domain model and produces a `ComplianceCheckResult` with coverage counts and summary.

# SEBA Point Expansion

Expands Schneider Electric SEBA point names into readable descriptions using Python acronym replacement.

## Workflow

1. Python replaces known SEBA acronyms using `acronyms.txt`.
2. Unknown abbreviations are preserved for review.

## Files

### Input
- `point_names.csv` - SEBA point names to expand
- `Known_Acronyms.txt` - Known SEBA acronym mappings


### Output
- `expanded_points.csv` - Contains partial and final expansions

## Acronym File Format

`acronyms.txt`

```python
{
    "ActvScn": "Active Scene",
    "Afdd": "Automated Fault Detection and Diagnostics",
    "Alm": "Alarm",
    "Spt": "Setpoint"
}
```
Notes
Keep acronym mappings updated as new SEBA points are identified.

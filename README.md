# SEBA_Acronym_Expander
Expands SEBA point names into readable descriptions using a local LLM.

## Files

Input:
- `point_names.csv` - Points to expand
- `SEBA_examples.txt` - Known SEBA mappings

Output:
- `expanded_points.csv`

## Format

SEBA examples:
Fcu1OaDprPosSptMin = Fan Coil Unit 1 Outside Air Damper Minimum Position Setpoint

A Python-based tool that uses a local LLM to expand Schneider Electric SEBA point names into readable descriptions. It retrieves similar SEBA examples as context, allowing the model to infer accurate HVAC/BMS terminology while avoiding large prompt sizes.

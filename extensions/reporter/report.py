#!/usr/bin/env python3
"""Torwart Report Generator – AAP JSON -> Markdown für PR"""
import json, sys, pathlib
if len(sys.argv)<2:
    print("usage: report.py <aap_result.json>"); sys.exit(1)
data=json.loads(pathlib.Path(sys.argv[1]).read_text())
md=f"""# Torwart AAP Report – {data.get('survival_assessment')}

- **Confidence:** {data.get('overall_confidence')}
- **Residual:** {data.get('residual')}
- **Intent:** {data.get('phase0_intent')}

## Survival Assessment
{data.get('survival_assessment')} – {data.get('stress_tested_diagnosis')}

## Boundary Map
- changeable: {data.get('boundary_map',{}).get('changeable')}
- resistant: {data.get('boundary_map',{}).get('systemically_resistant')}
"""
print(md)
pathlib.Path("torwart_report.md").write_text(md)
print("[+] Wrote torwart_report.md")

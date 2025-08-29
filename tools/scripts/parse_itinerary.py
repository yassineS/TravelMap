#!/usr/bin/env python3
"""
Parse the extracted PDF text snippet and produce a simple itinerary JSON: list of {start,end,city,display}
"""
import re
import sys
import json
from pathlib import Path

if len(sys.argv) < 2:
    print('Usage: parse_itinerary.py <extracted_json>', file=sys.stderr)
    sys.exit(2)

p = Path(sys.argv[1])
if not p.exists():
    print('MISSING_FILE', file=sys.stderr)
    sys.exit(3)

data = json.loads(p.read_text())
text = data.get('text_snippet','')

# Regex to match lines like: 04/09 - 05/09 Viana do Castelo Hotel Laranjeira - Hotel 2 ★
pattern = re.compile(r"(?m)^(\d{2}/\d{2})(?:\s*-\s*(\d{2}/\d{2}))?\s+(.+?)(?:Hotel|$)")
matches = pattern.findall(text)

itinerary = []
for m in matches:
    start = m[0]
    end = m[1] if m[1] else ''
    city_raw = m[2].strip()
    # cleanup trailing punctuation
    city = re.sub(r"[\-,]$","", city_raw).strip()
    # normalize common encoding issues
    city = city.replace('\u00c2','Â').replace('\u00f1','ñ')
    # display-friendly date
    if end:
        display = f"{start} - {end}"
    else:
        display = f"{start}"
    itinerary.append({"start": start, "end": end, "city": city, "display": display})

# If no matches found, try a looser pattern for lines like '13/09 - 14/09 Padrón Hotel Rosalía'
if not itinerary:
    pattern2 = re.compile(r"(?m)(\d{2}/\d{2})\s*-\s*(\d{2}/\d{2})\s+([A-Za-zÀ-ÖØ-öø-ÿ '\-]+)")
    for m in pattern2.findall(text):
        itinerary.append({"start": m[0], "end": m[1], "city": m[2].strip(), "display": f"{m[0]} - {m[1]}"})

# Fallback: try parse the UTR header date range and route
if not itinerary:
    m = re.search(r"UTR\d+:\s*(.+?)\s*\((\d{2}-[A-Za-z]{3}-\d{4})\s*-\s*(\d{2}-[A-Za-z]{3}-\d{4})\)", text)
    if m:
        route = m.group(1)
        start = m.group(2)
        end = m.group(3)
        # split route by -
        parts = [p.strip() for p in route.split('-')]
        for i, city in enumerate(parts):
            itinerary.append({"start": start, "end": end if i==len(parts)-1 else '', "city": city, "display": f"{start} - {end}"})

# write JSON
outp = {"itinerary": itinerary}
print(json.dumps(outp, ensure_ascii=False, indent=2))

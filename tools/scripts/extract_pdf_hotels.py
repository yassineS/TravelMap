#!/usr/bin/env python3
"""
Simple PDF text extractor and heuristic hotel-parser.
Writes JSON to stdout mapping city -> list of extracted paragraphs containing the city name.
"""
import sys
import json
from pathlib import Path
try:
    from pypdf import PdfReader
except Exception:
    print('MISSING_PYPDF', file=sys.stderr)
    raise

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n\n".join(pages)

# Heuristic: split into paragraphs and pick those mentioning a city
def parse_hotels(text, city_aliases):
    # Normalize line breaks, split into paragraphs by blank line
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    out = {k: [] for k in city_aliases}
    lowered_paras = [p.lower() for p in paras]

    for city, aliases in city_aliases.items():
        for i, p in enumerate(lowered_paras):
            for a in aliases:
                if a in p:
                    # return the original paragraph (not lowercased)
                    out[city].append(paras[i])
                    break
    return out

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: extract_pdf_hotels.py <pdf-file>', file=sys.stderr)
        sys.exit(2)
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print('PDF_NOT_FOUND', file=sys.stderr)
        sys.exit(3)
    text = extract_text(pdf_path)

    # cities to search (map keys match the itinerary in the HTML)
    city_aliases = {
        'Adelaide': ['adelaide'],
        'Doha': ['doha'],
        'Vienna': ['vienna', 'wien'],
        'Salzburg': ['salzburg'],
        'Isen': ['isen'],
        'Tubingen': ['tubingen', 'tübingen'],
        'Basel': ['basel', 'bâle'],
        'Rabat': ['rabat'],
        'Geneva': ['geneva', 'genève', 'geneve'],
        'Lausanne': ['lausanne'],
        'Interlaken': ['interlaken'],
        'Zurich': ['zurich', 'zürich']
    }

    parsed = parse_hotels(text, city_aliases)
    # Also include a raw text sample to help debugging (first 6000 chars)
    result = {
        'by_city': parsed,
        'text_snippet': text[:6000]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

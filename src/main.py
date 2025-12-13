from parse.parser import parse_gmc_history
from util import get_history_bytes

raw_hist = get_history_bytes()
records = parse_gmc_history(raw_hist)

PREVIEW = 20
for r in records:
    print(r.ts.isoformat(), r.save_type, "tube=", r.tube)
    for segment in r.segments:
        print("  ", segment.mode, segment.values[:PREVIEW], f"... ({len(segment.values)} total)")

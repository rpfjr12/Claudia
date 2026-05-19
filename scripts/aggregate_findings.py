import json
import glob
import os

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "scan_results.json")

def aggregate_findings():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    all_items = []

    for f in files:
        try:
            with open(f, "r") as infile:
                data = json.load(infile)
                if isinstance(data, list):
                    all_items.extend(data)
        except Exception as e:
            print(f"[aggregate] Skipping {f}: {e}")

    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(all_items, outfile, indent=2)

    print(f"[aggregate] Wrote {len(all_items)} findings to {OUTPUT_FILE}")

if __name__ == "__main__":
    aggregate_findings()

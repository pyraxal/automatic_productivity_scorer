# Compact takes a directory of processed transcripts and converts them into a singular csv file
# Compact also can take a singular .csv file and convert it into a compact csv file

import os
import sys
import pandas as pd


def parse_productivity_column(csv_path):

    df = pd.read_csv(csv_path, header=None, names=["value"])
    data = df["value"].fillna("").astype(str).tolist()

    headers = [
        "Article Productivity",
        "Auxiliary Productivity",
        "Active Progressive Productivity",
        "General Progressive Productivity"
    ]

    sections = {h: [] for h in headers}
    current_header = None

    for line in data:
        line = line.strip()

        if line in headers:
            current_header = line
            continue

        if current_header is None:
            continue

        if line == "":
            current_header = None
            continue

        try:
            num = int(line)
            sections[current_header].append(num)
        except:
            pass

    for h in headers:
        if len(sections[h]) > 0:
            sections[h] = sections[h][:-1]

    return {
        "Total Article Productivity": sum(sections["Article Productivity"]),
        "Total Auxiliary Productivity": sum(sections["Auxiliary Productivity"]),
        "Total Active Progressive Productivity": sum(sections["Active Progressive Productivity"]),
        "Total General Progressive Productivity": sum(sections["General Progressive Productivity"])
    }


def is_ads_csv(csv_path):
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        return first_line.lower().startswith("utterance,ads")
    except:
        return False


def parse_ads_column(csv_path):

    df = pd.read_csv(csv_path)

    if "ADS" not in df.columns:
        return None

    total_utts = len(df)
    total_ads = int(df["ADS"].sum())
    ratio = total_ads / total_utts if total_utts > 0 else 0

    return {
        "Total ADS": total_ads,
        "Total Utterances": total_utts,
        "ADS Ratio": round(ratio, 4)
    }

def compact_single(csv_path):

    base = os.path.splitext(os.path.basename(csv_path))[0]

    if is_ads_csv(csv_path):
        totals = parse_ads_column(csv_path)
    else:
        totals = parse_productivity_column(csv_path)

    out_df = pd.DataFrame([{
        "Name": base,
        **totals
    }])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, f"{base}_compact.csv")

    out_df.to_csv(output_path, index=False)
    print(f"[OK] Compact file written: {output_path}")


def compact_directory(dir_path):

    rows = []

    for fname in os.listdir(dir_path):

        if not fname.lower().endswith((".csv", ".txt")):
            continue

        fpath = os.path.join(dir_path, fname)

        if is_ads_csv(fpath):
            totals = parse_ads_column(fpath)
        else:
            totals = parse_productivity_column(fpath)

        rows.append({
            "Name": os.path.splitext(fname)[0],
            **totals
        })

    result = pd.DataFrame(rows)

    base = os.path.basename(os.path.normpath(dir_path))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, f"{base}_compact.csv")

    result.to_csv(output_path, index=False)
    print(f"[OK] Directory compact file written: {output_path}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python compact.py file.csv")
        print("  python compact.py folder/")
        sys.exit(0)

    path = sys.argv[1]

    if os.path.isfile(path):
        compact_single(path)
    elif os.path.isdir(path):
        compact_directory(path)
    else:
        print(f"Error: path {path} not found.")
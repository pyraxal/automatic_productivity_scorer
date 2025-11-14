#Compact takes a directory of processed transcripts and converts them into a singular csv file
#Compact also can take a singular .csv file and convert it into a compact csv file
#The csv/txt is structured like so:
#Name, Total Article Productivity, Total Auxiliary Productivity, Total Active Progressive Productivity, Total General Progressive Productivity
#...,...,...,...,...

import os
import sys
import pandas as pd


def parse_column(csv_path):

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

    # Drop the last printed total
    for h in headers:
        if len(sections[h]) > 0:
            sections[h] = sections[h][:-1]

    return {
        "Total Article Productivity": sum(sections["Article Productivity"]),
        "Total Auxiliary Productivity": sum(sections["Auxiliary Productivity"]),
        "Total Active Progressive Productivity": sum(sections["Active Progressive Productivity"]),
        "Total General Progressive Productivity": sum(sections["General Progressive Productivity"])
    }


def compact_single(csv_path):

    # base name of input file
    base = os.path.splitext(os.path.basename(csv_path))[0]

    totals = parse_column(csv_path)

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
        if not fname.lower().endswith(".csv") and not fname.lower().endswith(".txt"):
            continue

        fpath = os.path.join(dir_path, fname)
        totals = parse_column(fpath)

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

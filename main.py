import argparse
import os
import glob
import shutil
from interface import run_full_pipeline, run_ads_only_pipeline


def main():
    parser = argparse.ArgumentParser(description="Process CHA or Text transcripts")
    parser.add_argument(
        "-p", "--path",
        default=None,
        help="Input file or folder to process (default: ./input/)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory for CSV results (default: ./output/)"
    )
    parser.add_argument(
        "-rr", "--extract-rr",
        default=False,
        action="store_true",
        help="Extract only RR lines for analysis"
    )
    parser.add_argument(
        "-ads", "--ads-only",
        default=False,
        action="store_true",
        help="Run ADS-only analysis (active declarative sentences only)"
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_dir = args.path or os.path.join(base_dir, "input")
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created input folder: {input_dir}")

    if os.path.isfile(input_dir):
        files = [input_dir]
        base_input_dir = os.path.dirname(input_dir)
    elif os.path.isdir(input_dir):
        files = glob.glob(os.path.join(input_dir, "*.cha")) + \
                glob.glob(os.path.join(input_dir, "*.txt"))
        base_input_dir = input_dir
    else:
        print(f"Error: {input_dir} is not a valid file or directory.")
        return

    if not files:
        print(f"No .cha or .txt files found in {input_dir}")
        return

    output_dir = args.output or os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    done_dir = os.path.join(base_dir, "processed")
    os.makedirs(done_dir, exist_ok=True)

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_csv = os.path.join(output_dir, base_name + "_results.csv")

        print(f"Processing {file_path} → {output_csv}")

        if args.ads_only:
            run_ads_only_pipeline(
                text,
                output_csv_path=output_csv,
                extract_rr=args.extract_rr
            )
        else:
            run_full_pipeline(
                text,
                output_csv_path=output_csv,
                extract_rr=args.extract_rr
            )

        print(f"CSV written: {output_csv}")

        dest_path = os.path.join(done_dir, os.path.basename(file_path))
        shutil.move(file_path, dest_path)
        print(f"Moved processed file to: {dest_path}")


if __name__ == "__main__":
    main()
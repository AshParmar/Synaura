import json
from pathlib import Path
import sys

def merge_json_files(input_dir, output_file):
    input_dir = Path(input_dir)
    all_results = []
    for file in sorted(input_dir.glob('results_*.json')):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
                else:
                    print(f"Warning: {file} does not contain a list, skipping.")
            except Exception as e:
                print(f"Error reading {file}: {e}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"Merged {len(all_results)} results into {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Merge batch result JSON files into one.")
    parser.add_argument('--input_dir', type=str, default="results/final_reports_imedrag", help='Directory with batch result files')
    parser.add_argument('--output', type=str, default="results/final_reports_imedrag/all_results.json", help='Output merged JSON file')
    args = parser.parse_args()
    merge_json_files(args.input_dir, args.output)

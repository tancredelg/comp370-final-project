import pandas as pd
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help='json file with data')
    args = parser.parse_args()
    filename = args.file
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    filename = ".."+filename.strip(".json")
    # Save DataFrame to CSV file
    df.to_csv(filename + '.csv', index=False)

if __name__ == "__main__":
    main()
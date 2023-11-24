import argparse
import pandas as pd

def remove_duplicates(input_file, output_file):
    df = pd.read_csv(input_file)

    # Remove rows with duplicate titles, keeping the first occurrence
    df.drop_duplicates(subset='title', keep='first', inplace=True)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Rows with duplicate titles removed. Output saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remove rows with duplicate titles from a CSV file')
    parser.add_argument('-input', type=str, help='Input CSV file name')
    parser.add_argument('-output', type=str, help='Output CSV file name')
    args = parser.parse_args()

    remove_duplicates(args.input, args.output)

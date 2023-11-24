import argparse
import json
import os
from pathlib import Path
from newsapi import fetch_top_headlines

data_dir = Path(__file__).parent.parent / 'data'
if not Path.exists(data_dir):
    Path.mkdir(data_dir)

if not Path.exists(data_dir / 'headlines'):
    Path.mkdir(data_dir / 'headlines')


def collect_top_headlines(api_key: str, country: str, category: str, keywords_file=None, append=True):
    # Without keywords
    if keywords_file is None:
        news = fetch_top_headlines(api_key, country, category)

        if news is None:
            return

        output_file = Path(data_dir / 'headlines' / f'all_{category}_headlines.json')

        if append and Path.exists(output_file) and os.stat(output_file).st_size > 0:
            with open(output_file, 'r', encoding='utf-8') as existing_file:
                existing_data = json.load(existing_file)
                existing_data.extend(news)
                news = existing_data

        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(news, json_file, ensure_ascii=False, indent=4)

        print(f"Collected all top {category} headlines in the country '{country}'"
              f" and saved it in {Path(output_file).relative_to(data_dir.parent)}")
        return

    # With keywords
    with open(keywords_file, 'r', encoding='utf-8') as file:
        keyword_sets = json.load(file)

    for keyword_set in keyword_sets:
        for set_name, keywords in keyword_set.items():
            news = fetch_top_headlines(api_key, country, category, keywords)

            if news is None:
                continue

            output_file = Path(data_dir / 'headlines' / f'{set_name}_{category}_headlines.json')

            if append and Path.exists(output_file) and os.stat(output_file).st_size > 0:
                with open(output_file, 'r', encoding='utf-8') as existing_file:
                    existing_data = json.load(existing_file)
                    existing_data.extend(news)
                    news = existing_data

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(news, json_file, ensure_ascii=False, indent=4)

            print(f"Collected top {category} headlines for '{set_name}' in the country '{country}'"
                  f" and saved it in {Path(output_file).relative_to(data_dir.parent)}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Collects top headlines using NewsAPI. Output files are stored"
                    f" in the 'data' directory (same level as the 'scripts' directory).\n\n"
                    f"Example usage:\npython -m collect_entertainment -a ******** -c us -k keyword_sets.json",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-a", "--api-key",
                        required=True,
                        help="Your NewsAPI API key.")
    parser.add_argument("-c", "--country",
                        default='us',
                        help="The 2-letter ISO 3166-1 code of the country you want to get headlines for."
                             " Default is 'us'.")
    parser.add_argument("-k", "--keyword-sets",
                        default=None,
                        help="The JSON file containing the sets of keywords or phrases to search for in"
                             " each article title and description.")

    args = parser.parse_args()

    collect_top_headlines(args.api_key, args.country, 'entertainment', keywords_file=args.keyword_sets)


if __name__ == "__main__":
    main()

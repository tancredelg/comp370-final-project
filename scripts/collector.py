import argparse
import datetime
import json
import os
from pathlib import Path
from newsapi import fetch_news

data_dir = Path(__file__).parent.parent / 'data'
if not Path.exists(data_dir):
    Path.mkdir(data_dir)

if not Path.exists(data_dir / 'articles'):
    Path.mkdir(data_dir / 'articles')


def collect_news(api_key: str, start_date: datetime.date, end_date: datetime.date, keywords_file, language='en', search_title_only=False, append=True):
    with open(keywords_file, 'r', encoding='utf-8') as file:
        keyword_sets = json.load(file)

    for keyword_set in keyword_sets:
        for set_name, keywords in keyword_set.items():
            news = fetch_news(api_key,
                              start_date,
                              end_date,
                              keywords=keywords,
                              language=language,
                              search_title_only=search_title_only)

            if news is None:
                continue

            #news = json.loads('[{"source": {"id": null, "name": "me.com"}, "author": "tancrede", "title": "‘Killers of the Flower Moon’", "description": "new article about Killers of the Flower Moon",'
            #                  ' "publishedAt": "2023-11-01"}]')

            output_file = Path(data_dir / 'articles' / f'{set_name}_articles.json')

            if append and os.stat(output_file).st_size > 0:
                with open(output_file, 'r', encoding='utf-8') as existing_file:
                    existing_data = json.load(existing_file)
                    existing_data.extend(news)
                    news = existing_data

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(news, json_file, ensure_ascii=False, indent=4)

            print(f"Collected news for {set_name} from {start_date} to {end_date}"
                  f" and saved it in {Path(output_file).relative_to(data_dir.parent)}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Collects news articles using NewsAPI. Output files are stored"
                    f" in the 'data' directory (same level as the 'scripts' directory).\n\n"
                    f"Example usage:\npython -m collector -a ******** -k keyword_sets.json -d 2023-11-17 --title-only",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-a", "--api-key",
                        required=True,
                        help="Your NewsAPI API key.")
    parser.add_argument("-s", "--start-date",
                        default=datetime.date.today().strftime('%Y-%m-%d'),
                        help="The date the search should start from. Default is today.")
    parser.add_argument("-e", "--end-date",
                        default=datetime.date.today().strftime('%Y-%m-%d'),
                        help="The date the search should end with. Default is today.")
    parser.add_argument("-k", "--keyword-sets",
                        required=True,
                        help="The JSON file containing the sets of keywords or phrases to search for in"
                             " each article title and description.")
    parser.add_argument("-l", "--language",
                        type=str,
                        default='en',
                        help="The 2-letter ISO-639-1 code of the language you want to get headlines for."
                             " Possible options: ar de en es fr he it nl no pt ru sv ud zh. Default is 'en'.")
    parser.add_argument("-t", "--title-only",
                        action='store_true',
                        help="Only search for the keywords in the article title.")

    args = parser.parse_args()

    collect_news(args.api_key,
                 datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date(),
                 datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date(),
                 args.keyword_sets,
                 language=args.language,
                 search_title_only=args.title_only)


if __name__ == "__main__":
    main()

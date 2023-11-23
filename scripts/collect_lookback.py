import argparse
import datetime
import json
from pathlib import Path
from newsapi import fetch_news_lookback

def collect_news(api_key: str, lookback_days: int, keywords_file, language='en', search_title_only=False, append=False):
    with open(keywords_file, 'r', encoding='utf-8') as file:
        keyword_sets = json.load(file)

    for keyword_set in keyword_sets:
        for set_name, keywords in keyword_set.items():
            news = fetch_news_lookback(api_key,
                                       lookback_days,
                                       keywords=keywords,
                                       language=language,
                                       search_title_only=search_title_only)

            output_file = Path(data_dir / 'articles' / f'{set_name}_articles.json')

            if append:
                with open(output_file, 'r', encoding='utf-8') as existing_data:
                    existing_data = json.load(json_file)
                    news.extend(existing_data)

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(news, json_file, ensure_ascii=False, indent=4)

            print(f"Collected news for {set_name} from the last {lookback_days} days"
                  f" and saved it in {Path(output_file).relative_to(data_dir.parent)}")



def main():
    parser = argparse.ArgumentParser(
        description=f"Run a specified collector.py command for each of the last 30 days."
                    f" WARNING: this will call the API n times, for each keyword set in your keywords json file.\n\n"
                    f"Example usage:\npython -m collector -a ******** -k keyword_sets.json --title-only",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-a", "--api-key",
                        required=True,
                        help="As specified in collector.py")
    parser.add_argument("-k", "--keyword-sets",
                        required=True,
                        help="As specified in collector.py")
    parser.add_argument("-l", "--language",
                        type=str,
                        default='en',
                        help="As specified in collector.py")
    parser.add_argument("-t", "--title-only",
                        action='store_true',
                        help="As specified in collector.py")

    args = parser.parse_args()

    date = datetime.date.today()
    collect_news(args.api_key, date, args.keyword_sets, language=args.language, search_title_only=args.title_only, append=False)
    for i in range(1, 31):
        date = date - datetime.timedelta(days=1)
        collect_news(args.api_key, date, args.keyword_sets, language=args.language, search_title_only=args.title_only, append=True)


if __name__ == "__main__":
    main()

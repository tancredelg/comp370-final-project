import argparse
import datetime

from collector import collect_news


def main():
    parser = argparse.ArgumentParser(
        description=f"Run a specified collector.py command for each of the last 30 days."
                    f" WARNING: this will call the API 30 FOR EACH KEYWORD SET in your keywords json file.\n\n"
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

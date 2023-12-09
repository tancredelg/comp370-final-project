import argparse
import json
import re
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

THRESHOLD_FREQUENCY = 1


def remove_punctuation(article_description: str) -> str:
    # Replace punctuation with a space.
    article_description = article_description.replace('&quot;', '')
    article_description = re.sub('‘', "'", article_description)
    article_description = re.sub('’', "'", article_description)
    article_description = re.sub('“', '"', article_description)
    article_description = re.sub('”', '"', article_description)
    chars_to_replace = '()[],-.?!:;#&/"—'
    for c in chars_to_replace:
        if c in article_description:
            article_description = article_description.replace(c, ' ')

    article_description = re.sub('…', '...', article_description)
    return article_description


def count_word_freq_per_topic(csv_filepath) -> dict[int, dict[str, int]]:
    df = pd.read_csv(csv_filepath, encoding='utf-8')
    word_freq_by_topic = {}

    df.reset_index()
    for index, row in df.iterrows():
        try:
            #topic = TOPICS[int(row['Annotation']) - 1]
            topic = row['Annotation']
        except ValueError:
            topic = "null/duplicate"

        try:
            description = str(row['Description'])
        except ValueError:
            description = ''

        if topic not in word_freq_by_topic:
            word_freq_by_topic[topic] = defaultdict(int)

        description = remove_punctuation(description)
        words = description.lower().split()
        description_word_freq = Counter(words).most_common()

        for word, freq in description_word_freq:
            word_freq_by_topic[topic][word] += freq

    # Remove words with frequencies below the threshold.
    for topic_word_freq in word_freq_by_topic.values():
        for word, freq in dict(topic_word_freq).items():
            if freq < THRESHOLD_FREQUENCY:
                del topic_word_freq[word]

    # Sort topics alphabetically, and sort words by frequency (decreasing).
    word_freq_by_topic = dict(sorted(word_freq_by_topic.items(), key=lambda i: i[0]))
    for topic, topic_word_freq in word_freq_by_topic.items():
        word_freq_by_topic[topic] = dict(sorted(topic_word_freq.items(), key=lambda i: i[1], reverse=True))

    return word_freq_by_topic


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True, help="The path to the output json file.")
    parser.add_argument("-a", "--articles", required=True, help="The path to the articles csv file.")
    args = parser.parse_args()

    word_frequencies = count_word_freq_per_topic(args.articles)

    output_file = Path(args.output)
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(word_frequencies, file, indent=4)


if __name__ == '__main__':
    main()

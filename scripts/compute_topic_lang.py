import argparse
import json
import math
from collections import Counter


# tfidf(word, topic, word_freq_by_topic) = tf(word, topic) * idf(word, articles)
#   tf(word, topic) = the number of occurrences of  <word> in articles about <topic>
#   idf(word, articles) = log( <number of topics> / <number of topics that used <word>> )
def tfidf(word: str, topic: str, word_freq_by_topic: dict[str, dict[str, int]]) -> float:
    tf = word_freq_by_topic[topic].get(word, 0)

    # Collect all the topics that used <word>, using their word frequency dictionaries.
    topics_that_used_word = []
    for topic, topic_word_freq in word_freq_by_topic.items():
        if word in topic_word_freq.keys():
            topics_that_used_word.append(topic)

    idf = math.log(len(word_freq_by_topic) / len(topics_that_used_word))
    return tf * idf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--topic-counts", required=True,
                        help="The path to the json file containing the word frequency for each topic.")
    parser.add_argument("-n", "--num-words", required=True, type=int,
                        help="The number of words by highest TF-IDF score to output for each topic.")
    parser.add_argument("--show-scores", action='store_true', default=False,
                        help="Show the tf-idf score for each word.")
    args = parser.parse_args()

    # Load word frequency json file back into a nested dictionary.
    with open(args.topic_counts, 'r') as file:
        word_freq_by_topic: dict[str, dict[str, int]] = json.load(file)

    # Compute tfidf scores for all words and then store top n words in output dictionary.
    top_words_by_topic: dict[str, [dict[str, float] | str]] = {}
    for topic, topic_word_freq in word_freq_by_topic.items():
        tfidf_scores: dict[str, float] = {}
        for word in topic_word_freq.keys():
            tfidf_scores[word] = tfidf(word, topic, word_freq_by_topic)

        top_words = dict(Counter(tfidf_scores).most_common(args.num_words))
        if not args.show_scores:
            top_words = list(top_words.keys())

        top_words_by_topic[topic] = top_words

    print(json.dumps(top_words_by_topic, indent=4))


if __name__ == '__main__':
    main()

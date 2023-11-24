import json

import requests
from datetime import datetime


def fetch_news(api_key: str, start_date: datetime.date, end_date: datetime.date, keywords: list, language='en', search_title_only=False):
    """
Fetch news articles from the NewsAPI 'everything' endpoint, with the request parameters specified.
    :param api_key: The api key to use for the NewsAPI request.
    :param start_date: The date to start the search from.
    :param end_date: The date to end the search at.
    :param keywords: The list of keywords or phrases to search for in the article title and body
    :param language: The language of the news.
    :param search_title_only: Only search for the keywords in the article title.
    :return: The list of articles obtained from the request.
    """
    if len(keywords) < 1:
        raise ValueError("keywords must include at least 1 keyword.")

    if end_date < start_date:
        raise ValueError("end_date cannot be before start_date.")

    if end_date > datetime.today().date():
        raise ValueError("end_date cannot be after today.")

    # Define the parameters for the API request
    params = {
        'apiKey': api_key,
        'q': ' OR '.join(keywords),  # Combine multiple keywords with 'OR' for a broader search
        'language': language,
        'sortBy': 'publishedAt',
        'from': start_date,
        'to': end_date
    }

    if search_title_only:
        params['searchIn'] = 'title'

    try:
        response = requests.get('https://newsapi.org/v2/everything', params=params)

        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])

            total_results = news_data.get('totalResults')
            print(f"fetch_news: Found {total_results} articles matching your query.")
            total_to_get = get_article_count_from_user(total_results)
            print("total to get = ", total_to_get)
            pages_to_get = (total_to_get // 100) + 1

            print(f"fetch_news: Pages to fetch for this query: {pages_to_get}")
            for i in range(2, pages_to_get + 1):
                params['page'] = i
                print(f"fetch_news: fetching page {i}")
                response = requests.get('https://newsapi.org/v2/everything', params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles.extend(news_data.get('articles', []))
                else:
                    print("fetch_news: Failed to fetch additional pages of the request."
                          " Only the first 100 articles were saved.")

            print("fetch_news: Number of articles fetched: ", len(articles))
            filtered_articles = [a for a in articles if a['title'] != "[Removed]"]

            return filtered_articles
        else:
            print(f"fetch_news: Failed to fetch news:\n{response.text}")
            return None
    except Exception as e:
        print(f"fetch_news: An error occurred when fetching: {str(e)}")
        return None


def get_article_count_from_user(total_results):
    n = min(100, total_results)
    while True:
        try:
            n = int(input(f"fetch_news: How many of the articles would you like to fetch?"
                          f"(each get request can return up to 100, so >100 will require more requests)\n> "))
        except Exception as e:
            print("fetch_news: Please enter a valid whole number.")
            continue

        if 1 <= n <= total_results:
            break

        print(f"fetch_news: The number must be between 1 and {total_results}")

    return n

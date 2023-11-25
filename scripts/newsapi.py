import time

import requests
from datetime import datetime


def fetch_news(api_key: str, start_date: datetime.date, end_date: datetime.date, keywords: list, language='en', search_title_only=False):
    """
Fetch news articles from the NewsAPI 'everything' endpoint, with the request parameters specified.
    :param api_key: The api key to use for the NewsAPI request.
    :param start_date: The date to start the search from.
    :param end_date: The date to end the search at.
    :param keywords: The list of keywords or phrases to search for in the article title and body.
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
        'q': ' OR '.join(keywords),  # Combine multiple keywords with 'OR' for a broader search
        'language': language,
        'sortBy': 'publishedAt',
        'from': start_date,
        'to': end_date
    }

    if search_title_only:
        params['searchIn'] = 'title'

    return get_news(api_key, '/v2/everything', params)


def fetch_top_headlines(api_key: str, country: str, category: str, keywords=None):
    """
Fetch current trending news articles using the NewsAPI 'top-headlines' endpoint, with the request parameters specified.
    :param api_key: The api key to use for the NewsAPI request.
    :param country: The 2-letter ISO 3166-1 code of the country you want to get headlines for.
    :param category: The category you want to get headlines for.
    :param keywords: The list of keywords or phrases to search for in the article title and body.
    :return: The list of articles obtained from the request.
    """
    if len(country) != 2:
        raise ValueError("newsapi: Please specify the country using its 2-letter ISO 3166-1 code. E.g. 'us' or 'fr'")    

    # Define the parameters for the API request
    params = {
        'country': country,
        'category': category,
        'pageSize': 100  # default is 20, max is 100
    }

    if keywords is not None:
        if len(keywords) < 1:
            raise ValueError("newsapi: `keywords` must include at least 1 keyword.")

        params['q'] = ' OR '.join(keywords),  # Combine multiple keywords with 'OR' for a broader search

    return get_news(api_key, '/v2/top-headlines', params)


def get_news(api_key: str, endpoint: str, params) -> list | None:
    params['apiKey'] = api_key

    try:
        response = requests.get(f'https://newsapi.org{endpoint}', params=params)

        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])

            total_results = news_data.get('totalResults')
            print(f"newsapi: Found {total_results} articles matching your query.")
            if total_results < 1:
                return None

            total_to_get = get_article_count_from_user(total_results)
            pages_to_get = (total_to_get // 100) + 1

            print(f"newsapi: Pages to fetch for this query: {pages_to_get}")
            for i in range(2, pages_to_get + 1):
                params['page'] = i
                print(f"newsapi: fetching page {i} in 10 seconds (delay is too avoid getting rate limited by the api).")
                time.sleep(10)
                response = requests.get('https://newsapi.org/v2/everything', params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles.extend(news_data.get('articles', []))
                else:
                    print("newsapi: Failed to fetch additional pages of the request."
                          " Only the first 100 articles were saved.")
                    print(f"Error message:\n{response.text}")

            print("newsapi: Number of articles fetched: ", len(articles))
            filtered_articles = [a for a in articles if a['title'] != "[Removed]"]

            return filtered_articles
        else:
            print(f"newsapi: Failed to fetch news:\n{response.text}")
            return None
    except Exception as e:
        print(f"newsapi: An error occurred when fetching: {str(e)}")
        return None


def get_article_count_from_user(total_results):
    n = min(100, total_results)
    while True:
        try:
            n = int(input(f"newsapi: How many of the articles would you like to fetch?"
                          f" (each get request can return up to 100, so >100 will require more requests)\n> "))
        except Exception as e:
            print("newsapi: Please enter a valid whole number.")
            continue

        if 1 <= n <= total_results:
            break

        print(f"newsapi: The number must be between 1 and {total_results}")

    return n

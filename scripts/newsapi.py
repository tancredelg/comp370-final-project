import requests
from datetime import datetime, timedelta


def fetch_news(api_key: str, date: datetime.date, keywords: list, language='en', search_title_only=False) -> list | None:
    """
Fetch news articles from the NewsAPI 'everything' endpoint, with the request parameters specified.
    :param api_key: The api key to use for the NewsAPI request.
    :param date: The number of days to look back.
    :param keywords: The list of keywords or phrases to search for in the article title and body
    :param language: The language of the news.
    :param search_title_only: Only search for the keywords in the article title.
    :return: The list of articles obtained from the request.
    """
    if len(keywords) < 1:
        raise ValueError("keywords must include at least 1 keyword")

    days_diff = datetime.today().date() - date
    if days_diff > timedelta(days=30):
        raise ValueError("Date must be within the last 30 days.")

    # Define the parameters for the API request
    params = {
        'apiKey': api_key,
        'q': ' OR '.join(keywords),  # Combine multiple keywords with 'OR' for a broader search
        'language': language,
        'sortBy': 'publishedAt',
        'from': date
    }

    if search_title_only:
        params['searchIn'] = 'title'

    try:
        response = requests.get('https://newsapi.org/v2/everything', params=params)

        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])

            filtered_articles = [a for a in articles if a['title'] != "[Removed]"]

            return filtered_articles
        else:
            print(f"Failed to fetch news. Response: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred when fetching: {str(e)}")
        return None

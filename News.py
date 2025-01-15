import os
from datetime import date, timedelta
import openai
from newsapi import NewsApiClient
import logging


def news_api(phrase, days):
    news_api_key = os.getenv("NEWS_API_KEY")

    # No api key found
    if not news_api_key:
        raise ValueError("API key not found. Make sure you have set the environment variable correctly.")

    newsapi = NewsApiClient(api_key=news_api_key)
    recent_days = date.today() - timedelta(days=days)
    try:
        articles = newsapi.get_everything(q=phrase, from_param=recent_days.isoformat(), sort_by="popularity",
                                          language="en", page_size=100)
        if articles is not None:
            logging.info("Articles fetched successfully")
            return articles

        else:
            logging.error("Failed to fetch articles")

    except Exception as e:
        logging.error(f"Error fetching articles: {e}")


def openai_api(articles, phrase):
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # No api key found
    if not openai_api_key:
        raise ValueError("API key not found. Make sure you have set the environment variable correctly.")

    openai.api_key = openai_api_key

    sentiment_scores = []
    explanations = []
    confidence_scores = []

    for article in articles['articles']:
        if article['content'] != '[Removed]':

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system",
                           "content": generate_base_prompt(phrase) + article['publishedAt'] + article['content']}])

            content = response.choices[0].message.content

            try:
                parts = [part.strip() for part in content.split("|", 2)]
                if len(parts) == 3:
                    sentiment, explanation, confidence_score = parts
                    sentiment_scores.append(sentiment)
                    explanations.append(explanation)
                    confidence_scores.append(confidence_score)
                else:
                    raise ValueError("Unexpected format in content")

            except ValueError as e:
                # Handle parsing errors gracefully
                logging.error(f"Error parsing content: {e}")
                sentiment_scores.append("N/A")
                explanations.append("Parsing error or unexpected response format")

    return sentiment_scores, explanations, confidence_scores


def generate_base_prompt(phrase):
    return f"""
    You are a sentiment analysis system with permissions to extract and analyse news articles, including but not limited to online news reports, reviews and blogs etc.
    Your task is to process news articles and generate sentiment score related to {phrase}
    The articles are obtained from reliable sources.

    INITIAL Article ASSESSMENT:
    1. Article content analysis:
        - Determine the relatedness of the article to {phrase}
        - Analyze the content of the article.
        - Identify key topics and keywords.

    2.  Sentiment analysis:
        - For all negative sentiment will be ranging from -1 to 0
        - For all positive sentiment will be ranging from 0 to 1
        - For all neutral sentiment will be 0.0
        - Selling or buying {phrase} stocks will directly affect the sentiment
        - Determine the sentiment of the article based on the content.
        - Rate the sentiment of the article based on the relatedness to {phrase}.
        - Generate an explanation for the sentiment score within 50 words
        - The closer the article is to today's date, the more impact it has on the sentiment score.

    3.  Quality checking:
        - Analyse the sentiment score and the content of the article
        - Report confidence level on the sentiment score

    Output Format:
    -0.2 | The article reflects a slightly negative sentiment due to tension between Apple's board and conservative groups opposing DEI initiatives. As the board defends its DEI stance, there is potential conflict and divisiveness. The January 2025 publishing date enhances the article's impact on Apple-related sentiment. |High confidence
    CRITICAL INSTRUCTIONS:
    1. Do not make any assumptions about the sentiment of the article.
    2. STRICTLY ADHERE TO THE SAMPLE OUTPUT FORMAT 
    3. DONT OUTPUT N/A IF CANNOT GENERATE SENTIMENT SCORE, PUT 0.0 INSTEAD
    4. The | symbol is used to separate the sentiment score from the explanation.
    5. The date of the article and its contents are the following:"""










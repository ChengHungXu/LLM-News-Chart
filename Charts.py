import datetime
import openai
import time
import base64
from lightweight_charts import Chart
import News
import logging
import os

logging.basicConfig(level=logging.INFO)


def generate_base_prompt(sentiment_score):
    return f"""
    You are a chart analysis system with permission to analyse the provided chart.
    The chart provided is a 15 minutes timeframe chart. 
    Your task is to provide trading insights and key entry points using ICT concept.
    You can combine multiple indicators to generate your insights.
    The sentiment score will be ranging from -1 to 1 where -1 is very negative, 1 is very positive and 0 is neutral.
    Your sentiment score is :{sentiment_score}
    INITIAL Chart ASSESSMENT:
    1. Chart content analysis:
        - Determine support and resistance levels
        - Determine market trend pattern

    2.  Trading insights:
        - Trading signals and entry points based on the analysis
        - Apply ICT concept to the chart to generate trading insights.
        - INCORPRATE FVG, OB , Volume imbalance, MSS,sellside and buyside liquidity into the analysis
        - Analyse the chart for potential entry points using ICT concept.

    Summary:
    - Analyse the chart for potential entry points using ICT concept.
    - Provide long and short term entry points.
    - Consider the sentiment score which will affect the market trend.

    CRITICAL INSTRUCTIONS:
    1. Avoid using characters like '#*' in the output generation 
    2. NEGATIVE SENTIMENT WILL TEND TO MAKE THE MARKET BEARISH
    3. POSITIVE SENTIMENT WILL TEND TO MAKE THE MARKET BULLISH
    4. THE STRONGNESS OF THE SENTIMENT WILL DETERMINE THE MARKET TREND"""


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyse_chart(base_64_image, sentiment_score):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": [{
                       "type": "text",
                       "text": generate_base_prompt(sentiment_score=sentiment_score),
                   },
                       {
                           "type": "image_url",
                           "image_url": {"url": f"data:image/jpeg;base64,{base_64_image}"},
                       }, ]

                   }
                  ]
    )

    content = response.choices[0].message.content
    print(content)


def take_screenshot(key):
    img = chart.screenshot()
    t = time.time()
    with open(f"screenshot-{t}.jpeg", 'wb') as f:
        f.write(img)
    base64_image = encode_image(f'screenshot-{t}.jpeg')
    analyse_chart(base64_image, sentiment_score)


def average_sent_score(sentiment_scores):
    return sum(float(score) for score in sentiment_scores) / len(sentiment_scores)


if __name__ == '__main__':
    articles = News.news_api("AAPL", 3)
    sentiment_score, explanation, confidence_score = News.openai_api(articles, "AAPL")
    average_sentiment = average_sent_score(sentiment_score)
    chart = Chart()
    chart_api_key = os.getenv("CHART_API_KEY")
    chart.polygon.api_key(chart_api_key)

    chart.polygon.stock(
        symbol='AAPL',
        timeframe='15min',
        start_date=datetime.date.today() - datetime.timedelta(days=3))

    chart.topbar.button('screenshot', 'Screenshot', func=take_screenshot)
    chart.show(block=True)







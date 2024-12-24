from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import logging
from datetime import datetime


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Functions

def get_trending_news():
    try:
        url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=<ADD_YOUR_API_KEY_HERE>"
        response = requests.get(url)
        response.raise_for_status()
        page = response.json()
        articles = page.get("articles", [])
        results = [ar["title"] for ar in articles[:10]]
        if not results:
            return ["No news available at the moment."]
        return results
    except Exception as e:
        logging.debug(f"Error fetching news: {e}")
        return ["Failed to fetch news."]
    
def get_horoscope(sign_name):
    """Fetch and return horoscope for the specified sign."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        signs = {
            'aries': 1, 'taurus': 2, 'gemini': 3, 'cancer': 4,
            'leo': 5, 'virgo': 6, 'libra': 7, 'scorpio': 8,
            'sagittarius': 9, 'capricorn': 10, 'aquarius': 11, 'pisces': 12
        }
        sign_id = signs.get(sign_name.lower())
        if sign_id is None:
            return "Invalid sign."

        url = f'https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign={sign_id}'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        horoscope_text = soup.select_one('.main-horoscope p').get_text().strip()
        return horoscope_text.capitalize()
    except Exception as e:
        logging.debug(f"Error fetching horoscope: {e}")
        return "Failed to fetch horoscope."

def get_history_today():
    """Fetch and return historical events that happened on this day."""
    try:
        url = 'https://www.onthisday.com/'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        events = [event.getText().strip() for event in soup.select('.event')[:5]]
        return events or ["No historical events available."]
    except Exception as e:
        logging.debug(f"Error fetching history: {e}")
        return ["Failed to fetch historical events."]

def get_weather(location):
    try:
        api_key = "<ADD_YOUR_API_KEY_HERE>"
        url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_desc = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        humidity = data['current']['humidity']
        return f"{location}: {weather_desc}, {temp_c}°C, Humidity: {humidity}%"
    except Exception as e:
        logging.debug(f"Error fetching weather: {e}")
        return "Failed to fetch weather."

def get_daily_quote():
    try:
        api_key = "<ADD_YOUR_API_KEY_HERE>"
        category = "inspirational"
        url = f"https://api.api-ninjas.com/v1/quotes?category={category}"
        headers = {'X-Api-Key': api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            quote = data[0]['quote']
            author = data[0]['author']
            return f"{quote} - {author}"
        else:
            return "No quote available."
    except Exception as e:
        logging.debug(f"Error fetching quote: {e}")
        return "Failed to fetch quote."

def get_crypto_price(coin):
    try:
        api_key = "<ADD_YOUR_API_KEY_HERE>" 
        url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={coin}"
        headers = {'X-Api-Key': api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Check if the response contains the expected data
        price = data.get('price')
        symbol = data.get('symbol')
        timestamp = data.get('timestamp')

        if price and symbol and timestamp:
            # Ensure price is a float
            price = float(price)

            # Fetch the exchange rate from USD to INR
            exchange_rate = get_exchange_rates(base="USD", symbols="INR").get("INR", 1)
            price_in_inr = price * exchange_rate

            # Return both USD and INR prices
            return f"Price: {price:.2f} USD, {price_in_inr:.2f} INR, Symbol: {symbol}, Timestamp: {datetime.fromtimestamp(timestamp)}"
        else:
            return "Invalid data received from the API."
    except Exception as e:
        logging.debug(f"Error fetching crypto price for {coin}: {e}")
        return "Failed to fetch crypto price."

    
def get_exchange_rates(base="USD", symbols="EUR,INR,GBP"):
    """Fetch and return exchange rates."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url)
        response.raise_for_status()
        rates = response.json().get("rates", {})
        return {symbol: rates[symbol] for symbol in symbols.split(",")}
    except Exception as e:
        logging.debug(f"Error fetching exchange rates: {e}")
        return {}

def get_random_fact():
    """Fetch and return a random fact."""
    try:
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("text", "No fact available.")
    except Exception as e:
        logging.debug(f"Error fetching fact: {e}")
        return "Failed to fetch fact."

# Routes

@app.route("/")
def home():
    news = get_trending_news()
    horoscope = get_horoscope("sagittarius")
    history = get_history_today()
    weather = get_weather("New Delhi")
    quote = get_daily_quote()
    exchange_rates = get_exchange_rates()
    fact = get_random_fact()
    crypto = get_crypto_price("TRXUSD")

    return render_template(
        "index.html",
        news=news,
        horoscope=horoscope,
        history=history,
        weather=weather,
        quote=quote,
        exchange_rates=exchange_rates,
        fact=fact,
        crypto=crypto
    )

@app.route("/horoscope", methods=["GET", "POST"])
def horoscope_form():
    if request.method == "POST":
        sign = request.form.get("sign")
        horoscope = get_horoscope(sign)
        return render_template("horoscope.html", horoscope=horoscope)
    return render_template("horoscope_form.html")

if __name__ == "__main__":
    app.run(debug=True)
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

URL = "https://books.toscrape.com/"
BASE_CURRENCY = "GBP"
TARGET_CURRENCY = "KES"

try:
    # Scrape books
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")[:10]

    products = []

    # Get exchange rate
    rate_url = f"https://open.er-api.com/v6/latest/{BASE_CURRENCY}"
    rate_response = requests.get(rate_url, timeout=10)
    rate_response.raise_for_status()

    rate_data = rate_response.json()

    # Check if the API request was successful
    if rate_data.get("result") != "success":
        raise Exception("Failed to retrieve exchange rates.")

    exchange_rate = rate_data["rates"][TARGET_CURRENCY]

    # Timestamp (optional extension)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for book in books:
        title = book.h3.a["title"]
        price_text = book.find("p", class_="price_color").text

        # Extract the numeric part of the price
        price = float(re.search(r"\d+\.\d+", price_text).group())

        converted_price = round(price * exchange_rate, 2)

        products.append({
            "Product Name": title,
            f"Price ({BASE_CURRENCY})": price,
            f"Price ({TARGET_CURRENCY})": converted_price,
            "Converted On": timestamp
        })

    # Create DataFrame
    df = pd.DataFrame(products)

    # Display the table neatly
    print("\nConverted Book Prices:\n")
    print(df.to_string(index=False))

    # Save to CSV
    df.to_csv("converted_book_prices.csv", index=False)
    print("\nData saved to converted_book_prices.csv")

except requests.exceptions.ConnectionError:
    print("Connection error. Please check your internet connection.")

except requests.exceptions.Timeout:
    print("The request timed out. Try again later.")

except requests.exceptions.RequestException as e:
    print("Something went wrong while requesting data:", e)

except KeyError:
    print("Currency not found. Check if the currency code is correct.")


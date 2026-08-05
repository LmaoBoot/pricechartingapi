import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_product(url: str) -> dict:
    data = {
        "product_name": None,
        "product_image": None,
        "product_price": None,
    }

    try:
        page = requests.get(url, timeout=20)
        page.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"Failed to fetch URL: {exc}") from exc

    soup = BeautifulSoup(page.content, "html.parser")

    product_name = soup.find("h1", id="product_name")
    if product_name:
        name_text = product_name.text.strip().split(" \n")[0]
        data["product_name"] = name_text

    product_details = soup.find("div", id="product_details")
    if product_details:
        img = product_details.find("img")
        if img:
            data["product_image"] = img.get("src")

    product_price = soup.find("td", id="used_price")
    if product_price:
        price_span = product_price.find("span")
        if price_span:
            data["product_price"] = price_span.text.strip()

    if not data["product_name"] and not data["product_price"]:
        raise ValueError("Could not parse product data from page")

    return data


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/product")
def product():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing required query parameter: url"}), 400

    try:
        return jsonify(get_product(url))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
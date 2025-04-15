from flask import Flask, request, jsonify
import hmac, hashlib, json
from time import gmtime, strftime
import urllib.parse
import requests

ACCESS_KEY = "ad058d0a-8f0e-4a12-a5aa-344fe004c193"
SECRET_KEY = "5b9de2176368f4c2fab72a6fca8cac61aa01da7e"

app = Flask(__name__)

def generate_hmac(method, url_path):
    datetime_gmt = strftime('%y%m%dT%H%M%SZ', gmtime())
    message = datetime_gmt + method + url_path
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"CEA algorithm=HmacSHA256, access-key={ACCESS_KEY}, signed-date={datetime_gmt}, signature={signature}"

@app.route("/recommend")
def recommend():
    keyword = request.args.get("keyword", "무선 이어폰")
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://www.coupang.com/np/search?q={encoded_keyword}"

    deeplink_api = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    full_url = f"https://api-gateway.coupang.com{deeplink_api}"

    headers = {
        "Authorization": generate_hmac("POST", deeplink_api),
        "Content-Type": "application/json"
    }

    body = {
        "coupangUrls": [search_url]
    }

    res = requests.post(full_url, headers=headers, json=body)
    data = res.json()

    if "data" in data:
        return jsonify({
            "keyword": keyword,
            "link": data["data"][0]["shortenUrl"]
        })
    else:
        return jsonify({"error": "Link generation failed"}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

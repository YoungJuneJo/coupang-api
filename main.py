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

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # ✅ GPT가 보낸 제품 리스트를 JSON으로 받음
        body = request.get_json()
        keyword = body.get("keyword", "")
        products = body.get("products", [])  # [{ name: "제품명", summary: "...", ... }, ...]

        if not products:
            return jsonify({"error": "No product list provided"}), 400

        # ✅ 각 제품 이름으로 쿠팡 검색 URL 생성
        coupang_urls = [
            f"https://www.coupang.com/np/search?q={urllib.parse.quote(p['name'])}"
            for p in products
        ]

        # ✅ 전체 키워드 검색 링크도 추가
        search_url = f"https://www.coupang.com/np/search?q={urllib.parse.quote(keyword)}"
        coupang_urls.append(search_url)

        # ✅ 딥링크 API 호출
        deeplink_api = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
        full_url = f"https://api-gateway.coupang.com{deeplink_api}"
        headers = {
            "Authorization": generate_hmac("POST", deeplink_api),
            "Content-Type": "application/json"
        }
        payload = {
            "coupangUrls": coupang_urls
        }

        res = requests.post(full_url, headers=headers, json=payload)
        data = res.json()

        if "data" not in data or len(data["data"]) < len(products):
            return jsonify({"error": "Link generation failed"}), 500

        # ✅ 딥링크 결과 매핑
        for i, p in enumerate(products):
            p["link"] = data["data"][i]["shortenUrl"]

        return jsonify({
            "keyword": keyword,
            "products": products,
            "searchLink": data["data"][-1]["shortenUrl"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

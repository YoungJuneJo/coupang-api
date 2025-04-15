from flask import Flask, request, jsonify
import hmac, hashlib, json
from time import gmtime, strftime
import requests

# ✅ 본인의 쿠팡 API 키 정보 입력
ACCESS_KEY = "ad058d0a-8f0e-4a12-a5aa-344fe004c193"
SECRET_KEY = "5b9de2176368f4c2fab72a6fca8cac61aa01da7e"

app = Flask(__name__)

# HMAC 서명 생성 함수
def generate_hmac(method, url_path):
    datetime_gmt = strftime('%y%m%dT%H%M%SZ', gmtime())
    message = datetime_gmt + method + url_path
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"CEA algorithm=HmacSHA256, access-key={ACCESS_KEY}, signed-date={datetime_gmt}, signature={signature}"

# 추천 상품 API (딥링크 생성)
@app.route("/recommend")
def recommend():
    keyword = request.args.get("keyword", "무선 이어폰")
    search_url = f"https://www.coupang.com/np/search?q={keyword}"
    
    deeplink_api = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    full_url = f"https://api-gateway.coupang.com{deeplink_api}"

    headers = {
        "Authorization": generate_hmac("POST", deeplink_api),
        "Content-Type": "application/json"
    }

    body = {
        "coupangUrls": [search_url]
    }

    res = requests.post(full_url, headers=headers, data=json.dumps(body))
    print("응답 상태코드:", res.status_code)
    print("응답 내용:", res.text)
    data = res.json()

    if "data" in data:
        return jsonify({
            "keyword": keyword,
            "link": data["data"][0]["shortenUrl"]
        })
    else:
        return jsonify({"error": "Link generation failed"}), 500

# 앱 실행
if __name__ == "__main__":
    app.run(port=5000)

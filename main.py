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
    keyword = request.args.get("keyword", "무선 이어폰").lower()
    encoded_keyword = urllib.parse.quote(keyword)

    # ✅ 키워드 기반 상품 추천 분기
    if "노트북" in keyword:
        products = [
            {
                "name": "레노버 아이디어패드 Slim1",
                "summary": "라이젠 5 + 16GB, 256GB SSD 탑재, 가볍고 무난한 가성비 노트북",
                "review": "문서 작업, 인터넷, 인강용으로 인기 많아요"
            },
            {
                "name": "ASUS 비보북 S15 OLED",
                "summary": "고화질 OLED 디스플레이, 라이젠 7, 대용량 배터리",
                "review": "영상 편집이나 디자인 작업에도 적합해요"
            }
        ]
    elif "선풍기" in keyword:
        products = [
            {
                "name": "신일 리모컨 스탠드 선풍기",
                "summary": "조용하고 바람 강도 조절이 쉬운 전통 강자",
                "review": "리모컨 편리하고 바람도 시원해요"
            },
            {
                "name": "샤오미 미지아 무선 선풍기",
                "summary": "BLDC 모터, 무선 작동, 감성 디자인",
                "review": "조용하고 선도 깔끔해서 인테리어에 좋아요"
            }
        ]
    else:
        # 기본 이어폰 추천
        products = [
            {
                "name": "QCY T13 무선 이어폰",
                "summary": "가성비 좋고 배터리 오래감",
                "review": "리뷰가 10만 개 넘는 국민 이어폰"
            },
            {
                "name": "삼성 갤럭시 버즈2",
                "summary": "노이즈 캔슬링 탑재, 통화품질 우수",
                "review": "디자인이 예쁘고 착용감도 좋아요"
            }
        ]

    # 각 제품에 대해 쿠팡 검색 URL 생성
    coupang_urls = [
        f"https://www.coupang.com/np/search?q={urllib.parse.quote(product['name'])}"
        for product in products
    ]

    # 전체 검색 결과 링크도 포함
    search_url = f"https://www.coupang.com/np/search?q={encoded_keyword}"
    coupang_urls.append(search_url)

    # 딥링크 요청
    deeplink_api = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    full_url = f"https://api-gateway.coupang.com{deeplink_api}"
    headers = {
        "Authorization": generate_hmac("POST", deeplink_api),
        "Content-Type": "application/json"
    }
    body = {
        "coupangUrls": coupang_urls
    }

    res = requests.post(full_url, headers=headers, json=body)
    data = res.json()

    if "data" in data and len(data["data"]) >= len(products):
        # 딥링크 매핑
        for i in range(len(products)):
            products[i]["link"] = data["data"][i]["shortenUrl"]

        return jsonify({
            "keyword": keyword,
            "products": products,
            "searchLink": data["data"][-1]["shortenUrl"]  # 마지막은 전체 검색 링크
        })
    else:
        return jsonify({"error": "Link generation failed"}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

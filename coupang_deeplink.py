import hmac
import hashlib
import requests
import json
from time import gmtime, strftime

# Step 1: 본인의 키 입력
ACCESS_KEY = "ad058d0a-8f0e-4a12-a5aa-344fe004c193"
SECRET_KEY = "5b9de2176368f4c2fab72a6fca8cac61aa01da7e"

# Step 2: 검색 키워드 → 상품 URL
KEYWORD = "무선 이어폰"
PRODUCT_URLS = [
    f"https://www.coupang.com/np/search?q={KEYWORD}"
]

# Step 3: HMAC 인증 생성
def generate_hmac_signature(method, url_path, access_key, secret_key):
    datetime_gmt = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'
    path, *query = url_path.split("?")
    query_string = query[0] if query else ""
    message = datetime_gmt + method + path + query_string

    signature = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_gmt}, signature={signature}"

# Step 4: 딥링크 생성 요청
def create_deeplink(coupang_urls):
    method = "POST"
    url_path = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    full_url = f"https://api-gateway.coupang.com{url_path}"

    headers = {
        "Authorization": generate_hmac_signature(method, url_path, ACCESS_KEY, SECRET_KEY),
        "Content-Type": "application/json"
    }

    body = {
        "coupangUrls": coupang_urls
    }

    res = requests.post(full_url, headers=headers, data=json.dumps(body))
    return res.json()

# Step 5: 실행
if __name__ == "__main__":
    result = create_deeplink(PRODUCT_URLS)
    print(json.dumps(result, indent=2, ensure_ascii=False))

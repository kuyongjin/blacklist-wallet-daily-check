import requests
import pandas as pd
import os

# 깃허브 Secrets에 숨겨둔 Chainabuse API 키 불러오기
API_KEY = os.environ.get("CHAINABUSE_API_KEY")

def main():
    if not API_KEY:
        print("에러: Chainabuse API 키가 없습니다.")
        return

    print("Chainabuse(스캠/해킹) 데이터 수집 중...")
    
    # Chainabuse 최신 리포트 API (최대 100개씩 호출)
    url = "https://api.chainabuse.com/v0/reports"
    
    # Chainabuse는 보통 Basic Auth 방식으로 API 키를 사용합니다 (키를 아이디처럼 사용)
    headers = {
        "Accept": "application/json"
    }
    
    # 쿼리 파라미터: 페이지당 100개씩 최근 데이터 조회
    params = {
        "perPage": 100,
        "page": 1
    }

    try:
        # API 호출 (auth 부분에 API 키 입력)
        response = requests.get(url, headers=headers, params=params, auth=(API_KEY, ''))
        response.raise_for_status() # 오류 발생 시 예외 처리
        data = response.json()
        
        wallets = []
        for report in data:
            # 리포트 내에 포함된 해커/스캐머 지갑 주소 추출
            addresses = report.get("addresses", [])
            coin_type = report.get("cryptoTicker", "UNKNOWN")
            
            for address_info in addresses:
                address = address_info.get("address")
                if address:
                    # XBT -> BTC 변환 (일관성 유지)
                    if coin_type.upper() == "XBT":
                        coin_type = "BTC"
                    
                    wallets.append([f"{coin_type.upper()}(스캠/해킹 신고지갑)", address])
        
        # 데이터프레임 변환 및 중복 제거
        df = pd.DataFrame(wallets, columns=["코인명(Chainabuse)", "지갑주소"])
        df = df.drop_duplicates().sort_values(by=["코인명(Chainabuse)", "지갑주소"])

        # 파일 저장 (고정 파일명 덮어쓰기)
        output_name = "chainabuse_addresses.csv"
        df.to_csv(output_name, index=False, encoding='utf-8-sig')
        print(f"성공: {len(df)}개 스캠/해킹 지갑 추출 완료 ({output_name} 저장)")
        
    except Exception as e:
        print(f"API 호출 실패 또는 에러 발생: {e}")

if __name__ == "__main__":
    main()

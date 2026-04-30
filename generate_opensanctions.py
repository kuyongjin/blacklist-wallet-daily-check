import json
import urllib.request
import pandas as pd
from datetime import datetime

# OpenSanctions '제재(Sanctions)' 데이터셋 URL (스트리밍용 JSON)
url = "https://data.opensanctions.org/datasets/latest/sanctions/entities.ftm.json"

def main():
    print("OpenSanctions 데이터 다운로드 및 분석 중...")
    
    wallets = []
    req = urllib.request.Request(url)
    
    # 메모리 절약을 위해 스트리밍 방식으로 한 줄씩 읽어오기
    with urllib.request.urlopen(req) as response:
        for line in response:
            data = json.loads(line)
            
            # 스키마가 'CryptoWallet'인 데이터만 추출
            if data.get("schema") == "CryptoWallet":
                props = data.get("properties", {})
                
                # 주소와 코인 심볼 추출
                addresses = props.get("publicKey", [])
                currencies = props.get("currency", ["Unknown"])
                
                for addr in addresses:
                    for coin in currencies:
                        # XBT -> BTC 변환 (어제와 동일한 룰 적용)
                        if coin.upper() == "XBT":
                            coin = "BTC"
                            
                        wallets.append([f"{coin.upper()}(OS제재지갑)", addr])

    # 데이터프레임 변환 및 중복 제거
    df = pd.DataFrame(wallets, columns=["코인명(OpenSanctions)", "지갑주소"])
    df = df.drop_duplicates().sort_values(by=["코인명(OpenSanctions)", "지갑주소"])

    # 파일 저장 (오늘 날짜 포함)
    today = datetime.now().strftime('%Y%m%d')
    output_name = f"opensanctions_addresses_{today}.csv"
    
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    print(f"성공: {len(df)}개 주소 추출 완료 ({output_name} 저장)")

if __name__ == "__main__":
    main()

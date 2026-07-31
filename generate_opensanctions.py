import json
import urllib.request
import pandas as pd

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
                        coin = coin.upper()
                        
                        # 1. 주소 클렌징: 데스티네이션 태그 등 괄호 '(' 앞까지만 추출하고 공백 제거
                        clean_addr = addr.split("(")[0].strip()
                        
                        # 2. UNKNOWN 코인 추론 및 노이즈 제거 로직
                        if coin == "UNKNOWN":
                            if clean_addr.startswith("0x") and len(clean_addr) == 42:
                                coin = "EVM계열(ETH/BSC/POL/KAIA)" # 이더리움 및 확장 네트워크 통합
                            elif clean_addr.startswith(("1", "3", "bc1")) and 25 < len(clean_addr) < 90:
                                coin = "BTC"
                            elif clean_addr.startswith("T") and len(clean_addr) == 34:
                                coin = "TRX"
                            elif clean_addr.startswith("r") and 25 < len(clean_addr) < 36:
                                coin = "XRP"
                            else:
                                continue  # 어떤 패턴에도 맞지 않는 데이터(IMO 등)는 수집 제외
                        
                        # 3. XBT -> BTC 변환
                        elif coin == "XBT":
                            coin = "BTC"
                            
                        wallets.append([f"{coin}(OS제재지갑)", clean_addr])

    # 데이터프레임 변환 및 중복 제거
    df = pd.DataFrame(wallets, columns=["코인명(OpenSanctions)", "지갑주소"])
    df = df.drop_duplicates().sort_values(by=["코인명(OpenSanctions)", "지갑주소"])

    # 고정 파일명으로 저장 (매일 덮어쓰기)
    output_name = "opensanctions_addresses.csv"
    
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    print(f"성공: {len(df)}개 주소 추출 완료 ({output_name} 저장)")

if __name__ == "__main__":
    main()

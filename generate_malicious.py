import requests
import pandas as pd
import io

def main():
    print("글로벌 OSINT 위험 지갑 리스트 수집 시작...")
    malicious_wallets = []

    # 소스 1: CryptoscamDB (유명한 스캠 지갑 리스트)
    try:
        print("- 소스 1: CryptoscamDB 수집 중...")
        url_1 = "https://raw.githubusercontent.com/CryptoScamDB/blacklist/master/addresses.json"
        res = requests.get(url_1).json()
        for addr in res:
            malicious_wallets.append(["Scam/Fraud", addr.lower()])
    except:
        print("! 소스 1 수집 실패")

    # 소스 2: MyEtherWallet (MEW) 블랙리스트
    try:
        print("- 소스 2: MyEtherWallet 블랙리스트 수집 중...")
        url_2 = "https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/src/addresses/blacklisted-addresses.json"
        res = requests.get(url_2).json()
        for item in res:
            malicious_wallets.append(["Hacker/Malicious", item['address'].lower()])
    except:
        print("! 소스 2 수집 실패")

    # 소스 3: 보안 전문가 통합 리스트 (GitHub OSINT)
    try:
        print("- 소스 3: 보안 전문가 통합 리스트 수집 중...")
        # 전 세계 보안 커뮤니티에서 관리하는 피싱/스캠 주소들
        url_3 = "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/combined.json"
        res = requests.get(url_3).json()
        for addr in res:
            malicious_wallets.append(["Phishing/Scam", addr.lower()])
    except:
        print("! 소스 3 수집 실패")

    # 데이터 정리
    if malicious_wallets:
        df = pd.DataFrame(malicious_wallets, columns=["위험분류", "지갑주소"])
        # 주소 형식 정리 및 중복 제거
        df['지갑주소'] = df['지갑주소'].str.strip()
        df = df.drop_duplicates(subset=['지갑주소']).sort_values(by="위험분류")
        
        # CSV 저장
        output_name = "malicious_addresses.csv"
        df.to_csv(output_name, index=False, encoding='utf-8-sig')
        print(f"성공: 총 {len(df)}개의 위험 지갑 리스트 업데이트 완료 ({output_name})")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()

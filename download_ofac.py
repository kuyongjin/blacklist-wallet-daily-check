import cloudscraper

print("OFAC 리스트 다운로드 시도 중...")
scraper = cloudscraper.create_scraper() # 일반 브라우저로 위장
url = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.ZIP"

response = scraper.get(url)

if response.status_code == 200:
    with open("SDN_ADVANCED.ZIP", "wb") as f:
        f.write(response.content)
    print("다운로드 성공!")
else:
    print(f"다운로드 실패: 에러 코드 {response.status_code}")

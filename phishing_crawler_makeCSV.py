import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 크롤링할 대상 사이트 URL
base_url = 'https://phishtank.org/'
search_url = 'phish_search.php?page={}&valid=y&Search=Search'

# 각 게시물 페이지에서 실제 피싱 링크를 추출하는 함수


def extract_link(post_url):
    response = requests.get(post_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        padded_divs = soup.find_all('div', class_='padded')

        for padded_div in padded_divs:
            inner_div = padded_div.find('div', style=None, class_=None)
            if inner_div:
                span_element = inner_div.find('span')
                if span_element:
                    b_element = span_element.find('b')
                    if b_element:
                        link_text = b_element.text.strip()
                        # Cloudflare Email Protection 확인
                        if '[email protected]' in link_text:
                            return None  # 이메일 포함된 링크는 건너뜁니다
                        else:
                            return link_text
    return None

# 페이지마다 게시물을 크롤링하는 함수


def crawl_phish_tank(start_page, end_page):
    num = 0
    extracted_links = []

    for page in range(start_page, end_page + 1):
        url = urljoin(base_url, search_url.format(page))
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            post_elements = soup.select('div.padded table tr td:first-child a')

            for post_element in post_elements:
                post_link = urljoin(base_url, post_element['href'])
                extracted_link = extract_link(post_link)

                if extracted_link:
                    extracted_links.append({
                        'Extracted Link': extracted_link
                    })

        else:
            print(
                f"Error {response.status_code}: Failed to retrieve the webpage for page {page}.")

    return extracted_links

# CSV 파일로 저장하는 함수

def save_to_csv(data, filename='extracted_links.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Extracted Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in data:
            writer.writerow(item)


# 크롤링 실행 및 CSV 파일로 저장
extracted_data = crawl_phish_tank(0, 0)
save_to_csv(extracted_data, 'extracted_links.csv')
print("추출된 링크가 extracted_links.csv 파일에 저장되었습니다.")

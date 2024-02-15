import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

# 크롤링할 대상 사이트 URL
base_url = 'https://phishtank.org/'
search_url = 'phish_search.php?page={}&valid=y&active=y&Search=Search'

# Cloudflare 인코딩 된 이메일 디코딩하는 함수
def decode_cf_email(encoded_string):
    r = int(encoded_string[:2], 16)
    email = ''.join([chr(int(encoded_string[i:i+2], 16) ^ r) for i in range(2, len(encoded_string), 2)])
    return email

def extract_link(post_url):
    response = requests.get(post_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        b_element = soup.select_one('#widecol > div > div:nth-child(4) > span > b')

        if b_element:
            # Cloudflare로 보호된 이메일이 있는 경우 디코드
            cf_email = b_element.find(class_='__cf_email__')
            if cf_email and 'data-cfemail' in cf_email.attrs:
                encoded_email = cf_email['data-cfemail']
                decoded_email = decode_cf_email(encoded_email)
                cf_email.replace_with(decoded_email)
            link_text = b_element.get_text(strip=True)
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
                        'url': extracted_link
                    })
        else:
            print(
                f"Error {response.status_code}: Failed to retrieve the webpage for page {page}.")

    return extracted_links


# CSV 파일로 저장하는 함수
def save_to_csv(data, filename='extracted_links.csv', page=None):
    mode = 'a' if page > 0 else 'w' 
    header = page == 0
    
    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Extracted Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if header:
            writer.writeheader()
        for item in data:
            writer.writerow({'Extracted Link': item['url']})


for start_page in range(0, 25000):
    print(f"start: {start_page}") 
    extracted_data = crawl_phish_tank(start_page, start_page+1) 
    save_to_csv(extracted_data, 'test.csv', start_page)

print("추출된 링크가 extracted_links.csv 파일에 저장되었습니다.")

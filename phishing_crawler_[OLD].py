import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen

# 크롤링할 대상 사이트 URL
base_url = 'https://phishtank.org/'
search_url = 'phish_search.php?page={}&active=y&valid=y&Search=Search'

# 크롤링 헤더 설정
header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

# Cloudflare 인코딩 된 이메일 디코딩하는 함수


def decode_cf_email(encoded_string):
    r = int(encoded_string[:2], 16)
    email = ''.join([chr(int(encoded_string[i:i+2], 16) ^ r)
                    for i in range(2, len(encoded_string), 2)])
    return email


def extract_link(post_url):
    print("파라미터 URL checking =",post_url)
    response = requests.get(post_url, headers=header)
    print(response)
    # requests 상태 확인
    print("status_code = ", response.status_code)
    if response.status_code == 200:
        print("YES ITS OK")
        soup = BeautifulSoup(response.text, 'html.parser')
        b_element = soup.select_one(
            '#widecol > div > div:nth-child(4) > span > b')

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
    for page in range(start_page, end_page + 1):
        
        url = urljoin(base_url, search_url.format(page))
        response = requests.get(url, headers=header)

        if response.status_code == 200:
            print("code == 200")
            soup = BeautifulSoup(response.text, 'html.parser')
            post_elements = soup.select('div.padded table tr td:first-child a')

            for post_element in post_elements:
                #! 게시물 번호 확인 !#
                # print(post_element)
                post_link = urljoin(base_url, post_element['href'])
                #! 게시물 별 링크 확인 !#
                print("post_link =", post_link)
                extracted_link = extract_link(post_link)
                #######! 게시물 별 피싱링크 추출 !#######
                #######! 현재 extract_link가 !#######
                #######! 제대로 동작하지 않음.  !#######
                print("extracted_link =", extracted_link)

                if extracted_link:
                    num += 1
                    print(f"[+] DATA NUM {num}")
                    print(f"    |-- Page: {page}")
                    print(f"    |-- Post Link: {post_link}")
                    print(f"    |-- Extracted Link: {extracted_link}")
        else:
            print(
                f"Error {response.status_code}: Failed to retrieve the webpage for page {page}.")


# 크롤링 실행
crawl_phish_tank(8, 8)

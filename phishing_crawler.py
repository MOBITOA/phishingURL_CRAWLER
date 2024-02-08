import requests
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
                    num += 1
                    print("------------")
                    print(f"DATA NUM: {num}")
                    print(f"Page: {page}")
                    print(f"Post Link: {post_link}")
                    print(f"Extracted Link: {extracted_link}")

        else:
            print(
                f"Error {response.status_code}: Failed to retrieve the webpage for page {page}.")


# 크롤링 실행
crawl_phish_tank(1, 1)

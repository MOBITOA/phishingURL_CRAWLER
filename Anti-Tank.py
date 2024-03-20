import tkinter as tk
from tkinter import ttk, filedialog
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import tkinter.messagebox as msgbox

class PhishTankCrawlerGUI:
    def __init__(self, master):
        self.master = master
        master.title("҉--⌊ ANTI-TANK ⌉--҉")

        # Title Label
        self.title_label = ttk.Label(master, text="Anti-Tank", font=('Helvetica', 55, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # Title Image
        self.title_image = tk.PhotoImage(file="/Users/mobicom/Downloads/antiman.png")  # 이미지 파일 경로를 지정해주세요
        self.title_label_image = tk.Label(master, image=self.title_image)
        self.title_label_image.grid(row=0, column=3, padx=5, pady=5)

        # Start and End Page Entries
        self.start_page_label = ttk.Label(master, text="Start Page:")
        self.start_page_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky='e')
        self.start_page_entry = ttk.Entry(master, width=20)
        self.start_page_entry.grid(row=1, column=1, padx=5, pady=5, sticky='e')

        self.end_page_label = ttk.Label(master, text="End Page:")
        self.end_page_label.grid(row=1, column=2, padx=(5,5), pady=5, sticky='e')
        self.end_page_entry = ttk.Entry(master, width=20)
        self.end_page_entry.grid(row=1, column=3, padx=(5, 10), pady=5, sticky='w')

        # User-Agent Entry
        self.user_agent_label = ttk.Label(master, text="User-Agent:")
        self.user_agent_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.user_agent_entry = ttk.Entry(master, width=51)
        self.user_agent_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        # Cookies Entries
        self.cookies_labels = []
        self.cookies_entries = []
        self.cookie_names = ['PHPSESSID', '__cf_bm', '__cf_bm', 'cf_clearance']
        for i, cookie_name in enumerate(self.cookie_names):
            label = ttk.Label(master, text=f"{cookie_name}:")
            label.grid(row=i+4, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(master, width=51)
            entry.grid(row=i+4, column=1, columnspan=3, padx=5, pady=5, sticky='w')
            self.cookies_labels.append(label)
            self.cookies_entries.append(entry)

        # CSV File Location Entry
        self.csv_location_label = ttk.Label(master, text="CSV Location:")
        self.csv_location_label.grid(row=8, column=0, padx=5, pady=5, sticky='e')
        self.csv_location_entry = ttk.Entry(master, width=51)
        self.csv_location_entry.grid(row=8, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        # Browse Button
        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_location)
        self.browse_button.grid(row=9, column=0, columnspan=5, padx=5, pady=5)

        # Start Crawling Button
        self.start_button = ttk.Button(master, text="Start Crawling", command=self.start_crawling)
        self.start_button.grid(row=11, column=0, columnspan=5, padx=5, pady=5)

        # Crawling Status Label
        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=12, column=0, columnspan=5, padx=5, pady=5)

    def browse_location(self):
        filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                    filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))

        self.csv_location_entry.insert(0, filename)

    def extract_link(self, post_url, headers):
        response = requests.get(post_url, headers=headers)
        print(response)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            b_element = soup.select_one('#widecol > div > div:nth-child(4) > span > b')

            if b_element:
                link_text = b_element.get_text(strip=True)
                return link_text
        return None

    def crawl_phish_tank(self, start_page, end_page, headers):
        num = 1
        base_url = 'https://phishtank.org/'
        search_url = 'phish_search.php?page={}&active=y&valid=y&Search=Search'
        extracted_links = []

        for page in range(start_page, end_page + 1):
            url = urljoin(base_url, search_url.format(page))
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                post_elements = soup.select('div.padded table tr td:first-child a')

                for post_element in post_elements:
                    post_link = urljoin(base_url, post_element['href'])
                    extracted_link = self.extract_link(post_link, headers)

                    if extracted_link:
                        num += 1
                        extracted_links.append({'url': extracted_link})
            else:
                print(f"Error {response.status_code}: Failed to retrieve the webpage for page {page}.")

        return extracted_links

    def save_to_csv(self, data, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Extracted Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow({'Extracted Link': item['url']})

    def start_crawling(self):
        start_page = int(self.start_page_entry.get())
        end_page = int(self.end_page_entry.get())

        # Construct headers with user agent and cookies
        headers = {'User-Agent': self.user_agent_entry.get()}
        cookies = {self.cookie_names[i]: entry.get() for i, entry in enumerate(self.cookies_entries)}
        headers['Cookie'] = "; ".join([f"{name}={value}" for name, value in cookies.items()])

        extracted_data = self.crawl_phish_tank(start_page, end_page, headers)
        csv_location = self.csv_location_entry.get()

        self.save_to_csv(extracted_data, csv_location)
        print("추출된 링크가", csv_location, "파일에 저장되었습니다.")

        # Show completion message
        msgbox.showinfo("크롤링 완료", "크롤링이 완료되었습니다.")

def main():
    root = tk.Tk()
    root.resizable(False, False)  # 너비와 높이 모두 조정 불가능
    app = PhishTankCrawlerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

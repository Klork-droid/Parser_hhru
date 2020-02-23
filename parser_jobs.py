import requests
from bs4 import BeautifulSoup as bs
import csv
from datetime import datetime
from multiprocessing import Pool

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
headers = {'accept': '*/*',
           'user-agent': 'user_agent'}

base_url = "https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=true&employment=probation&enable_snippets=true&order_by=publication_time&text=python"


def hh_parse(base_url, headers):
    jobs = []
    urls = []
    session = requests.session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        request = session.get(base_url, headers=headers)
        soup = bs(request.content, 'lxml')
        try:
            pages = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            count = int(pages[-1].text)
            for i in range(count):
                url = f"{base_url}&page={i}"
                urls.append(url)
        except:
            print("first except")

        for url in urls:
            request = session.get(url, headers=headers)
            soup = bs(request.content, 'lxml')
            divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
            for div in divs:
                title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                jobs.append({
                    'title': title,
                    'href': f'=HYPERLINK("{href}")',
                    'company': company
                })
    else:
        print('ERROR')
    return jobs


def write_csv(jobs):
    with open('parsed_jobs.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(('Название вакансии', 'Ссылка', 'Название компании'))
        for job in jobs:
            writer.writerow((job['title'], job['href'], job['company']))


jobs = hh_parse(base_url, headers)
write_csv(jobs)

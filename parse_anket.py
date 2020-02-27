import requests
from bs4 import BeautifulSoup as bs
import csv
from multiprocessing import Pool

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
header = {'accept': '*/*',
          'user-agent': 'user_agent'}

base_url = "https://hh.ru/search/resume?text=Python&st=resumeSearch&logic=normal&pos=full_text&exp_period=all_time&text=github&st=resumeSearch&logic=normal&pos=full_text&exp_period=all_time&employment=probation&clusters=true&area=1&order_by=relevance&skill=1114&no_magic=false"


def get_all_links(base_url, headers):
    urls = []
    session = requests.session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            pages = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            count = int(pages[-1].text)
            for i in range(count):
                url = f"{base_url}&page={i}"
                urls.append(url)
        except:
            print("first except")
    else:
        print('ERROR')
    return urls


def get_resumes(url):
    resumes = []
    session = requests.session()
    request = session.get(url, headers=header)
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        divs = soup.find_all('div', attrs={'data-qa': 'resume-serp__resume-header'})
        for div in divs:
            find = div.find('a', attrs={'data-qa': 'resume-serp__resume-title'})
            if find:
                title = find.text
                href = find['href']
            else:
                find = div.find('a', attrs={'data-qa': 'resume-serp__resume-title resume-search-item__name_marked'})
                title = find.text
                href = find['href']
            href = href[:href.find("?")]
            resumes.append({
                'title': title,
                'href': f'https://hh.ru{href}'
            })
    else:
        print('ERROR')
    return resumes


def write_csv(resumes):
    with open('parsed_resumes.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for resume in resumes:
            writer.writerow((resume['title'], resume['href']))


def main():
    rewrite_csv()
    urls = get_all_links(base_url, headers=header)
    with Pool(60) as p:
       p.map(multiproc, urls)


def multiproc(url):
        resumes = get_resumes(url)
        write_csv(resumes)


def rewrite_csv():
    with open('parsed_resumes.csv', 'w+', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(('Название резюме', 'Ссылка'))


if __name__ == "__main__":
    main()

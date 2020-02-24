import requests
from bs4 import BeautifulSoup as bs
import csv
from multiprocessing import Pool
import traceback

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
header = {'accept': '*/*',
          'user-agent': 'user_agent'}


def get_url_from_csv():
    urls = []
    with open('parsed_resumes.csv', 'r', encoding="UTF-8") as file:
        for line in file.readlines():
            if line != "\n":
                begin = line.find('=HYPERLINK(""') + 13
                end = line.rfind('"")"')
                urls.append(line[begin:end])
    return urls


def get_github_links(url):
    print(url)
    link = ""
    end_index = []
    session = requests.session()
    request = session.get(url, headers=header)
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            div = str(soup.find('div', id="HH-Lux-InitialState"))
            begin = div.find("https://github.com/")
            if begin != -1:
                link = div[begin:]
                print(link)
                if link.find(".", 16) != -1:
                    end_index.append(link.find(".", 16))
                else:
                    end_index.append(len(link))
                for i in ["\\", '"', ' ', ')', ',', '?', ']']:
                    if link.find(i) != -1:
                        end_index.append(link.find(i))
                    else:
                        end_index.append(len(link))
                end = min(end_index)
                if end == len(link):
                    print(link)
                    print("Новый знак завершающий ссылку")
                else:
                    link = link[:end]
                    print(link)
            else:
                print('Ссылка отсутствует')
        except:
            traceback.print_exc()
            raise
    else:
        print('ERROR')

    return link


def main():
    urls = get_url_from_csv()
    with Pool(60) as p:
        p.map(multiproc, urls)


def multiproc(url):
    github_link = get_github_links(url)
    write_to_csv(github_link)


def write_to_csv(link):
    with open('github_links.csv', 'a', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow({link})


def rewrite_to_csv():
    with open('github_links.csv', 'w+', encoding="UTF-8") as file:
        pass


if __name__ == "__main__":
    rewrite_to_csv()
    main()
import requests
from bs4 import BeautifulSoup as bs
import csv
from multiprocessing import Pool
import traceback

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
header = {'accept': '*/*',
          'user-agent': 'user_agent'}

urls_github_links_dict = {}


def get_url_from_csv():
    urls = []
    i = 0
    with open('parsed_resumes.csv', 'r', encoding="UTF-8") as file:
        file.readline()
        for line in file.readlines():
            if len(line) > 3:
                begin = line.find('https')
                print(line[begin:-1])
                urls.append(line[begin:-1])
                #if i == 10:
                #    break
                #i += 1
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
            a = soup.find('div', class_="resume-block-container", attrs={'data-qa': "resume-block-skills-content"})
            if a is not None:
                a = a.text
                begin = a.find("https://github.com/")
                if begin != -1:
                    link = a[begin:]
                    # print(link[:50])
                    for i in ['\n', '"', ' ', ')', ',', '?', ']', '\\', ';', '.', '/', '\r']:
                        index = link.find(i, 21)
                        if index != -1:
                            end_index.append(index)
                        else:
                            end_index.append(len(link))
                    link = link[:min(end_index)]
                    # print(link)
                else:
                    link = '-'
                    print('Ссылка отсутствует')
            else:
                link = '-'
                print('Раздел "Обо мне" отсутствует')
        except:
            traceback.print_exc()
    else:
        print('ERROR')
    if link is None:
        print(link + "is None")
    return url, link


def main():
    rewrite_to_csv()
    urls = get_url_from_csv()
    #print(urls)
    with Pool(30) as p:
        p.map(multiproc, urls)


def multiproc(url):
    url_and_github_link = get_github_links(url)
    #print(url_and_github_link)
    write_to_csv(url_and_github_link)


def write_to_csv(url_and_github_link):
    with open('github_links.csv', 'a', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(url_and_github_link)
        print(url_and_github_link)


def add_github_links_to_resume():
    with open('github_links.csv', 'r', encoding="UTF-8") as file:
        for line in file.readlines():
            index = line.find("https")
            if index != -1:
                url_git = line.split(',')
                index2 = url_git[1].find('\n')
                if index2 != -1:
                    url_git[1] = url_git[1][:index2]
                urls_github_links_dict.update({url_git[0]: url_git[1]})
    with open('parsed_resumes.csv', 'r', encoding='utf-8') as file, open('all.csv', 'w+', encoding='utf-8') as file2:
        writer = csv.writer(file2)
        writer.writerow(('Название', 'hh.ru', 'github'))
        file.readline()
        for line in file.readlines():
            if len(line) > 3:
                #print(line)
                name_url = line.split(';')
                print(name_url)
                name_url[1] = name_url[1][:-1]
                print([name_url[1]])
                github_link = urls_github_links_dict.get(name_url[1])
                name_url.append(github_link)
                if name_url[2] is None:
                    print("None is                                                                         ", end="")
                print([name_url[2]])
                writer.writerow((name_url[0], name_url[1], name_url[2]))


def rewrite_to_csv():
    with open('github_links.csv', 'w+', encoding="UTF-8") as file:
        pass


if __name__ == "__main__":
    #print(get_github_links('https://hh.ru/resume/dd6aabab0007c167a90039ed1f6d3851653374'))
    main()
    add_github_links_to_resume()

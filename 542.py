import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process


def save_pdf(url, save_folder, poster_url=None):
    url = url.replace('arxiv.org/abs', 'arxiv.org/pdf')
    filename = url.split('/')[-1]
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    path = os.path.join(save_folder, filename)

    # print('save pdf')
    # print(path)
    # print(url)
    # print(poster_url)

    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

    if poster_url:
        with open(path.replace('.pdf', '.url'), 'w') as f:
            f.write('[InternetShortcut]\n')
            f.write('URL=%s' % poster_url)


def search_for_a_pdf(base_url):
    html = requests.get(base_url).content
    soup = BeautifulSoup(html, 'lxml')

    url = None
    if 'science.sciencemag.org' in base_url:
        for tag in soup.find_all('a'):
            if 'href' in tag.attrs:
                url = tag['href']
                if 'full-text.pdf' in url:
                    break
    else:
        for tag in soup.find_all('a'):
            if 'href' in tag.attrs:
                url = tag['href']
                if 'arxiv' in url:
                    break
                if url.endswith('.pdf'):
                    if 'Poster' in url:
                        # need to find paper pdf not the poster
                        continue
                    else:
                        break
    return urljoin(base_url, url)


def save_cell(cell, save_folder):
    poster_url = None
    if cell.a is not None:
        url = cell.a['href']
        if not url.startswith('http'):
            # not a link
            return
        if not url.endswith('pdf'):
            if 'arxiv' in url:
                pass
            else:
                # link needs attention
                # print('link needs attention')
                # print(save_folder)
                # print(url)
                poster_url = url
                url = search_for_a_pdf(url)
                # possible poster url
                # print(url)
                # print('-----')

        save_pdf(url, save_folder, poster_url=poster_url)


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def main():
    url = 'https://web.eecs.umich.edu/~fouhey/teaching/EECS542_F20/schedule.html'
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    folder = 'EECS542'
    create_dir(folder)
    processes = []

    for i in range(29):
        sub_folder = os.path.join(folder, 'class%s' % i)
        create_dir(sub_folder)
        row = soup.find('tr', 'r%s' % (i + 2))
        paper1_cell = row.find('td', 'c6')
        p = Process(target=save_cell, args=(paper1_cell, sub_folder))
        processes.append(p)
        p.start()
        paper2_cell = row.find('td', 'c7')
        p = Process(target=save_cell, args=(paper2_cell, sub_folder))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    main()


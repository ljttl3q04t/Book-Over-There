import requests
from bs4 import BeautifulSoup

from services.models import Book, Author, Publisher, Category


def fetch_remote_html(remote_url):
    try:
        headers = {
            'User-Agent': 'PostmanRuntime/7.29.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.get(remote_url, headers=headers)
        response.raise_for_status()  # Raise an exception for any unsuccessful response
        return response.text  # Return the HTML content
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


class CrawBase:
    DOMAIN_PREFIX = None
    soup = None

    def __init__(self, url):
        self.url = url
        self.book = {
            'book_name': '',
            'book_image': '',
            'book_category_name': '',
            'book_author_name': '',
            'book_publisher_name': '',
            'book_description': '',
        }

    def build_soup(self):
        if not self.url.startswith(self.DOMAIN_PREFIX):
            raise Exception('url is invalid')

        remote_html = fetch_remote_html(self.url)
        return BeautifulSoup(remote_html, 'lxml')

    def build_book(self):
        self.soup = self.build_soup()


class CrawTiki(CrawBase):
    DOMAIN_PREFIX = 'https://tiki.vn/'

    def build_book(self):
        super().build_book()
        breadcrumb = self.soup.find('div', class_='breadcrumb')
        if breadcrumb:
            a_breadcrumb = breadcrumb.find_all('a')
            self.book['book_name'] = a_breadcrumb[-1].text.strip()
            self.book['book_category_name'] = a_breadcrumb[-2].text.strip()

        link_tag = self.soup.select_one('link[as="image"][rel="preload"][type="image/webp"]')
        if link_tag:
            href = link_tag.get('href')
            self.book['book_image'] = href

        author_tag = self.soup.select_one('.brand-and-author a')
        if author_tag:
            book_author_name = author_tag.text.strip()
            if book_author_name.endswith(','):
                book_author_name = book_author_name.rstrip(',')
            self.book['book_author_name'] = book_author_name

        td_elements = self.soup.find_all('td')
        if td_elements:
            self.book['book_publisher_name'] = td_elements[-1].text.strip()

        try:
            self.book['book_description'] = self.soup.find_all('div', class_='content')[-1].find_all('p')[1].text.strip()
        except:
            pass

        return self.book


class CrawFahasa(CrawBase):
    DOMAIN_PREFIX = 'https://www.fahasa.com/'

    def build_book(self):
        super().build_book()
        a_element = self.soup.find('a', class_='include-in-gallery')
        if a_element:
            self.book['book_name'] = a_element.get('title')
            self.book['book_image'] = a_element.get('href')

        ol_element = self.soup.find('ol', class_='breadcrumb')
        if ol_element:
            last_li = ol_element.find_all('li')[-1]
            self.book['book_category_name'] = last_li.text.strip().rstrip('\n/').strip()

        author_element = self.soup.find('td', class_='data_author')
        if author_element:
            self.book['book_author_name'] = author_element.text.strip()

        publisher_element = self.soup.find('td', class_='data_publisher')
        if publisher_element:
            self.book['book_publisher_name'] = publisher_element.get_text().strip()

        description_elements = self.soup.find_all('p', style='text-align:justify')
        description = ''
        for p in description_elements:
            description += p.text + ' '
        book_description = description.strip()
        self.book['book_description'] = book_description
        return self.book

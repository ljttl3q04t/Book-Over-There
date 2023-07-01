import requests
from bs4 import BeautifulSoup

from services.models import Book, Author, Publisher


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

    def __int__(self, url):
        self.url = url
        self.book = Book()

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
        super(CrawTiki, self).build_book()


class CrawFahasa(CrawBase):
    DOMAIN_PREFIX = 'https://www.fahasa.com/'

    def build_book(self):
        super(CrawFahasa, self).build_book()
        a_element = self.soup.find('a', class_='include-in-gallery')
        if not a_element:
            return None
        self.book.name = a_element.get('title')
        self.book.image = a_element.get('href')

        author_element = self.soup.find('td', class_='data_author')
        if not author_element:
            return None
        author_name = author_element.text.strip()
        self.book.author, _ = Author.objects.get_or_create(name=author_name)

        publisher_element = self.soup.find('td', class_='data_publisher')
        if not publisher_element:
            return None
        publisher_name = publisher_element.get_text().strip()
        self.book.publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

        description_elements = self.soup.find_all('p', style='text-align:justify')
        description = ''
        for p in description_elements:
            description = p.text + ' '
        self.book.description = description
        return self.book

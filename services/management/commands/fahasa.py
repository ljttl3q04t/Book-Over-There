import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from services.models import Category, Book, Author, Publisher

MAP_CATEGORY = {
    'Văn học': 'https://www.fahasa.com/sach-trong-nuoc/van-hoc-trong-nuoc.html',
    'Kinh Tế': 'https://www.fahasa.com/sach-trong-nuoc/kinh-te-chinh-tri-phap-ly.html',
    'Tâm Lý - Kỹ năng sống': 'https://www.fahasa.com/sach-trong-nuoc/tam-ly-ky-nang-song.html',
    'Nuôi Dạy Con': 'https://www.fahasa.com/sach-trong-nuoc/nuoi-day-con.html',
    'Tiểu Sử Hồi Ký': 'https://www.fahasa.com/sach-trong-nuoc/tieu-su-hoi-ky.html',
}

def read_html_file(file_path='/home/tintin/PycharmProjects/book_over_there/services/management/commands/fahasa.html'):
    try:
        with open(file_path, 'r') as file:
            html_string = file.read()
        return html_string
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def fetch_remote_html(url):
    try:
        headers = {
            'User-Agent': 'PostmanRuntime/7.29.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for any unsuccessful response
        return response.text  # Return the HTML content
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions or errors
        print(f"Error: {e}")
        return None

def get_total_page():
    remote_url = 'https://www.fahasa.com/sach-trong-nuoc.html?order=created_at&limit=48&p=1'
    remote_html = fetch_remote_html(remote_url)
    soup = BeautifulSoup(remote_html, "lxml")
    page_div = soup.find('div', id='pagination')
    page_li = page_div.find_all('li')
    end_page_li = page_li[-2]
    if end_page_li:
        return int(end_page_li.text)
    return 0

def worker():
    total_page = get_total_page()
    print(total_page)
    for page in range(1, total_page + 1):
        current_progress = 1.0 * page / total_page * 100
        print("progress: {} %. current page: {}. Current time: {}"
              .format(current_progress, page, datetime.datetime.now()))

        remote_url = 'https://www.fahasa.com/sach-trong-nuoc.html?order=created_at&limit=48&p={page}'.format(page=page)
        remote_html = fetch_remote_html(remote_url)
        soup = BeautifulSoup(remote_html, "lxml")
        ule_product = soup.find('ul', id='products_grid')
        if ule_product:
            for li_element in ule_product.find_all('li'):
                book = Book()
                a_tag = li_element.find('a')
                if a_tag:
                    book.name = a_tag['title']
                    if book.name.startswith('Bộ sách') or book.name.startswith('Combo'):
                        continue
                    if Book.objects.filter(name=book.name).first():
                        continue
                    book_detail_url = a_tag['href']
                    book_detail_html = fetch_remote_html(book_detail_url)
                    book_detail_soup = BeautifulSoup(book_detail_html, 'lxml')
                    book_category = book_detail_soup.find('div', id="ves-breadcrumbs")
                    if book_category:
                        category_lis = book_category.find_all('li')
                        if category_lis:
                            category_li = category_lis[1]
                            if category_li:
                                book_category = category_li.text.strip().split('\n')[0]
                                category, _ = Category.objects.get_or_create(name=book_category)
                                book.category = category
                    author = book_detail_soup.find('td', class_='data_author')
                    if author:
                        book.author, _ = Author.objects.get_or_create(name=author.get_text().strip())
                    publisher = book_detail_soup.find('td', class_='data_publisher')
                    if publisher:
                        book.publisher, _ = Publisher.objects.get_or_create(name=publisher.get_text().strip())
                img_tag = li_element.find('img')
                if img_tag:
                    book.image = img_tag['data-src']

                try:
                    book.save()
                except Exception as err:
                    pass
                    # print(err)
                    # print("save failed: ", book)

class Command(BaseCommand):
    help = "crawl books from fahasa and store to database"

    def handle(self, *args, **options):
        worker()

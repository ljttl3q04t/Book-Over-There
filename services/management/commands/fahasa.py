from bs4 import BeautifulSoup
from django.core.management import BaseCommand
import requests
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


class Command(BaseCommand):
    help = "crawl books from fahasa and store to database"

    def handle(self, *args, **options):
        for k, v in MAP_CATEGORY.items():
            category, _ = Category.objects.get_or_create(name=k)
            for page in range(1, 3):
                remote_url = '{url}?order=num_orders_year&limit=48&p={page}'.format(url=v, page=page)
                print('remote_url', remote_url)
                remote_html = fetch_remote_html(remote_url)
                soup = BeautifulSoup(remote_html, "lxml")
                ule_product = soup.find('ul', id='products_grid')
                if ule_product:
                    for li_element in ule_product.find_all('li'):
                        book = Book()
                        book.category = category
                        a_tag = li_element.find('a')
                        if a_tag:
                            book.name = a_tag['title']
                            book_detail_url = a_tag['href']
                            print(book.name, book_detail_url)
                            if Book.objects.filter(name=book.name).first():
                                continue
                            book_detail_html = fetch_remote_html(book_detail_url)
                            book_detail_soup = BeautifulSoup(book_detail_html, 'lxml')
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
                        except:
                            print("save failed: ", book)

                        print('save book: ', book)

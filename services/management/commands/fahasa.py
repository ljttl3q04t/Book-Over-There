from bs4 import BeautifulSoup
from django.core.management import BaseCommand
import requests


def read_html_file(file_path='/home/tintin/Desktop/fahasa.html'):
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
        # remote_html = fetch_remote_html('https://www.fahasa.com/sach-trong-nuoc/kinh-te-chinh-tri-phap-ly.html')
        remote_html = read_html_file()
        soup = BeautifulSoup(remote_html, "lxml")
        soup.find()
        print(soup)

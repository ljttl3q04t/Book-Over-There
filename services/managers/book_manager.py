import requests
from django.core.files import File
from io import BytesIO


def save_image_from_url(book, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        file_content = BytesIO(response.content)
        filename = image_url.split("/")[-1]
        book.image.save(filename, File(file_content), save=True)

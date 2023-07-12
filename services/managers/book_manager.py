from io import BytesIO

import requests
from django.core.files import File

from services.managers.cache_manager import simple_cache_data, CACHE_KEY_CATEGORY_INFOS_DICT, \
    CACHE_KEY_AUTHOR_INFOS_DICT, combine_key_cache_data, CACHE_KEY_BOOK_INFOS, CACHE_KEY_PUBLISHER_INFOS_DICT
from services.models import Book, Author, Category, Publisher
from services.serializers import CategorySerializer, AuthorSerializer, BookSerializer, PublisherSerializer

def save_image_from_url(book, image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        file_content = BytesIO(response.content)
        filename = image_url.split("/")[-1]
        book.image.save(filename, File(file_content), save=True)

@simple_cache_data(**CACHE_KEY_AUTHOR_INFOS_DICT)
def get_author_infos():
    authors = Author.objects.all()
    serializer = AuthorSerializer(instance=authors, many=True)
    return {item['id']: item for item in serializer.data}

@simple_cache_data(**CACHE_KEY_CATEGORY_INFOS_DICT)
def get_category_infos():
    categories = Category.objects.all()
    serializer = CategorySerializer(instance=categories, many=True)
    return {item['id']: item for item in serializer.data}

@simple_cache_data(**CACHE_KEY_PUBLISHER_INFOS_DICT)
def get_publisher_infos():
    publishers = Publisher.objects.all()
    serializer = PublisherSerializer(instance=publishers, many=True)
    return {item['id']: item for item in serializer.data}

def get_book_records(book_ids=None, author_ids=None, category_ids=None):
    return Book.objects.filter_ignore_none(
        id__in=book_ids,
        author_id__in=author_ids,
        category_id__in=category_ids,
    )

@combine_key_cache_data(**CACHE_KEY_BOOK_INFOS)
def get_book_infos(book_ids):
    if not book_ids:
        return {}
    books = get_book_records(book_ids=book_ids)

    map_author = get_author_infos()
    map_category = get_category_infos()
    map_publisher = get_publisher_infos()
    result = {}

    for book in books:
        result[book.id] = {
            'name': book.name,
            'category': map_category.get(book.category_id),
            'author': map_author.get(book.author_id),
            'publisher': map_publisher.get(book.publisher_id),
            'description': book.description,
            'image': book.image.url if book.image else None,
        }
    return result

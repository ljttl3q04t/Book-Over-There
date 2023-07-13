from io import BytesIO

import requests
from django.core.files import File

from services.managers.cache_manager import delete_simple_cache_data, simple_cache_data, CACHE_KEY_CATEGORY_INFOS_DICT, \
    CACHE_KEY_AUTHOR_INFOS_DICT, combine_key_cache_data, CACHE_KEY_BOOK_INFOS, CACHE_KEY_PUBLISHER_INFOS_DICT, \
    invalid_cache_data
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

def get_book_records(book_ids=None, author_ids=None, category_ids=None, book_name=None):
    return Book.objects.filter_ignore_none(
        id__in=book_ids,
        author_id__in=author_ids,
        category_id__in=category_ids,
        name__istartswith=book_name,
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

def get_or_create_author(author_name):
    author, created = Author.objects.get_or_create(name=author_name)
    if created:
        invalid_cache_data(CACHE_KEY_AUTHOR_INFOS_DICT['cache_prefix'])
    return author

def get_or_create_category(category_name):
    category, created = Category.objects.get_or_create(name=category_name)
    invalid_cache_data(CACHE_KEY_CATEGORY_INFOS_DICT['cache_prefix'])
    return category

def create_book(name, category, author, image):
    author = get_or_create_author(author)
    category = get_or_create_category(category)
    return Book.objects.create(
        name=name,
        category=category,
        author=author,
        image=image,
    )

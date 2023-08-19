from django.test import TestCase
from rest_framework import status

from services.models import Book, Category, Author, BookClub
from d_free_book.models import ClubBook

from django.urls import reverse

class BotTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')
        self.author = Author.objects.create(name='author1')
        self.club = BookClub.objects.create(name='club1')
        self.book = Book.objects.create(name='book1', author=self.author, category=self.category)

    def test_get_book_list(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

    def test_get_club_list(self):
        response = self.client.get(reverse('book-club-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_club_book(self):
        ClubBook.objects.create(book=self.book, club=self.club, code='TEST-1', init_count=1, current_count=1)
        response = self.client.post(reverse('club-book-get-ids'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_club_book_infos(self):
        ClubBook.objects.create(book=self.book, club=self.club, code='TEST-1', init_count=1, current_count=1)
        club_book_ids = ClubBook.objects.flat_list('id')
        data = {'club_book_ids': ','.join(str(club_book_id) for club_book_id in club_book_ids)}
        response = self.client.post(reverse('club-book-get-infos'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sign_up(self):
        data = {
            'username': 'test',
            'password': '123456',
            'phone_number': '0333111222',
            'email': 'dungphse151526@fpt.edu.vn',
            'full_name': 'pham hoang dung',
        }
        response = self.client.post(reverse('user-register'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        data = {
            'username': 'test',
            'password': '123456',
            'phone_number': '0333111222',
            'email': 'dungphse151526@fpt.edu.vn',
            'full_name': 'pham hoang dung',
        }
        response = self.client.post(reverse('user-register'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('login'), data=data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

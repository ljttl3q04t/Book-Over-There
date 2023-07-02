from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('overview', views.OverViewAPIView.as_view(), name='overview'),

    # user
    path('user/register', views.UserRegisterView.as_view(), name='user-register'),
    path('user/login', views.UserLoginView.as_view(), name='login'),
    path('user/logout', views.LogoutView.as_view(), name='logout'),
    path('user/info', views.UserInfoView.as_view(), name='user-info'),
    path('user/info/update', views.UpdateUserInfoView.as_view(), name='update-user-info'),
    path('user/my-book', views.MyBookView.as_view(), name='view-my-book'),
    path('user/membership', views.MyMembershipView.as_view(), name='view-my-membership'),
    path('user/book/add', views.MyBookAddView.as_view(), name='user-add-book'),
    path('user/book/share-club', views.BookShareClubView.as_view(), name='share-book-to-club'),
    path('user/book/borrowing', views.UserBorrowingBookView.as_view(), name='user-view-borrowing-book'),

    # path('user/book/history', views.BookHistoryView.as_view(), name='book-history-view'),

    path('category/list', views.CategoryListView.as_view(), name='view-category'),

    # book and book copies
    path('book/<int:book_id>/update/', views.BookUpdateAPIView.as_view(), name='book-update'),
    path('book/check', views.BookCheckView.as_view(), name='book-check'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path('book-copies/create/', views.BookCopyCreateAPIView.as_view(), name='book-copy-create'),
    path('bookcopies/<int:pk>/', views.BookCopyUpdateView.as_view(), name='bookcopy-update'),

    # club
    path('club/list/', views.BookClubListAPIView.as_view(), name='book-club-list'),
    path('club/request-join', views.BookClubRequestJoinView.as_view(), name='book-club-request-join'),
    path('club/member/list', views.BookClubMemberView.as_view(), name='view-book-club-member'),
    path('club/member/update', views.BookClubMemberUpdateView.as_view(), name='update-book-club-member'),

    path('club/member/book/deposit', views.BookClubMemberBookDepositView.as_view(), name='member-deposit-book'),
    path('club/member/book/withdraw', views.BookClubMemberBookWithdrawView.as_view(), name='member-withdraw-book'),
    # path('club/member/book/lend', views.BookClubMemberBookLendView.as_view(), name='user-borrow-book'),
    # path('club/member/book/return', views.BookClubMemberBookReturnView.as_view(), name='member-return-book'),

    path('club/member/order/create', views.BookClubStaffCreateOrderView.as_view(), name='staff-create-order'),

    path('club/book/list', views.BookClubBookListView.as_view(), name='book-club-view-club-books'),
    path('club/staff/book/list', views.ClubBookListAPIView.as_view(), name='staff-view-all-books'),

    # membership-order
    path('membership/order/create', views.MemberShipOrderCreateView.as_view(), name='membership-order-create'),

    # order
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:order_id>/', views.GetOrderCreateAPIView.as_view(), name='order-detail'),

    # orderDetail
    path('order-details/create/', views.GetOrderCreateAPIView.as_view(), name='order-detail-create'),

    # upload file
    path('upload', views.UploadFileView.as_view(), name='upload-file'),
]

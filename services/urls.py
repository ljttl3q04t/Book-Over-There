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

    # book and book copies
    path('book/<int:book_id>/update/', views.BookUpdateAPIView.as_view(), name='book-update'),
    path('book/list/', views.BookListAPIView.as_view(), name='book-list'),
    path('book-copies/create/', views.BookCopyCreateAPIView.as_view(), name='book-copy-create'),
    path('bookcopies/<int:pk>/', views.BookCopyUpdateView.as_view(), name='bookcopy-update'),

    # club
    path('club/list/', views.BookClubListAPIView.as_view(), name='book-club-list'),
    path('club/request-join', views.BookClubRequestJoinView.as_view(), name='book-club-request-join'),

    # membership-order
    path('membership/order/create', views.MemberShipOrderCreateView.as_view(), name='membership-order-create'),

    # order
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('orders/<int:order_id>/', views.GetOrderCreateAPIView.as_view(), name='order-detail'),

    # orderDetail
    path('order-details/create/', views.GetOrderCreateAPIView.as_view(), name='order-detail-create'),

    # staff permission
    path('club/member/list', views.BookClubMemberListView.as_view(), name='book-club-member-list'),
]

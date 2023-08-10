from django.urls import path

from d_free_book import views

urlpatterns = [
    path('club_book/get_ids', views.ClubBookGetIdsView.as_view()),
    path('club_book/get_infos', views.ClubBookGetInfosView.as_view()),
    path('club_book/add', views.ClubBookAddView.as_view()),
    path('club_book/update', views.ClubBookUpdateView.as_view()),

    path('member/get_ids', views.MemberGetIdsView.as_view()),
    path('member/get_infos', views.MemberGetInfosView.as_view()),
    path('member/add', views.MemberAddView.as_view()),
    path('member/update', views.MemberUpdateView.as_view()),

    path('order/get_ids', views.StaffGetOrderIdsView.as_view()),
    path('order/get_infos', views.OrderInfosView.as_view()),
    path('order/create', views.OrderCreateView.as_view()),
    path('order/create/new_member', views.OrderCreateNewMemberView.as_view()),
    path('order/return_books', views.OrderReturnBooksView.as_view()),
    path('order/create/from_draft', views.OrderCreateFromDraftView.as_view()),
    path('order/create/from_draft/new_member', views.OrderCreateFromDraftNewMemberView.as_view()),

    path('order/draft/get_ids', views.GetDraftOrderIdsView.as_view()),
    path('order/draft/get_infos', views.GetDraftOrderInfosView.as_view()),
    path('order/draft/create', views.DraftOrderCreateOnlineView.as_view()),
    path('order/draft/update', views.DraftOrderUpdateOnlineView.as_view()),

    path('user/order_history', views.UserOrderHistoryView.as_view()),

    path('report', views.ReportView.as_view()),
]

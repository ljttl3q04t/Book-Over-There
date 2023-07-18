from django.contrib import admin
from django.core.cache import cache

from services import models
from d_free_book import models as dfb_models

class CustomModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.clear()

models_to_register = [
    models.Permission,
    models.Book,
    models.BookCopy,
    models.Publisher,
    models.Category,
    models.User,
    models.Author,
    models.BookClub,
    models.Membership,
    models.Member,
    models.MemberBookCopy,
    models.UploadFile,
    models.BookCopyHistory,
    models.MembershipOrder,
    models.MembershipOrderDetail,
    dfb_models.DFreeMember,
    dfb_models.ClubBook,
    dfb_models.DFreeOrder,
    dfb_models.DFreeOrderDetail,
]

for model in models_to_register:
    admin.site.register(model, CustomModelAdmin)

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

class UserAdmin(admin.ModelAdmin):
    search_fields = ('username', )  # Add fields you want to search on

class MembershipAdmin(admin.ModelAdmin):
    search_fields = ('member__user__username', )

models_to_register = [
    models.Permission,
    models.Book,
    models.BookCopy,
    models.Publisher,
    models.Category,
    models.Author,
    models.BookClub,
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
    dfb_models.DFreeDraftOrder,
]

for model in models_to_register:
    admin.site.register(model, CustomModelAdmin)

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Membership, MembershipAdmin)

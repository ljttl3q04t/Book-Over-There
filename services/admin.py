from django.contrib import admin

from services import models

admin.site.register(models.Permission)
admin.site.register(models.Book)
admin.site.register(models.BookCopy)
admin.site.register(models.Publisher)
admin.site.register(models.Category)
admin.site.register(models.User)
admin.site.register(models.Author)
admin.site.register(models.BookClub)
admin.site.register(models.Membership)
admin.site.register(models.Member)
admin.site.register(models.MemberBookCopy)
admin.site.register(models.UploadFile)
admin.site.register(models.BookCopyHistory)


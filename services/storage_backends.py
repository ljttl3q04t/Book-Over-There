from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage(S3Boto3Storage):
    def url(self, name, *args, **kwargs):
        url = super().url(name, *args, **kwargs)
        url = url.split('?')[0]
        return url


class BaseStaticStorage(CustomS3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False


class UserAvatarStorage(BaseStaticStorage):
    location = 'user_avatar'


class BookCoverStorage(BaseStaticStorage):
    location = 'book_cover'


class BookHistoryStorage(BaseStaticStorage):
    location = 'book_history'

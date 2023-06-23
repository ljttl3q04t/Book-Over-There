from storages.backends.s3boto3 import S3Boto3Storage


class BaseStaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False


class UserAvatarStorage(BaseStaticStorage):
    location = 'user_avatar'

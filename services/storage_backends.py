from storages.backends.s3boto3 import S3Boto3Storage


class PublicStaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False

bind = '127.0.0.1:8000'
workers = 4
worker_class = 'gevent'
max_requests = 1000
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
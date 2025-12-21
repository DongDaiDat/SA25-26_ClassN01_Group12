from .settings import *

# Dùng Postgres trong container đã publish ra host:5432
DATABASES['default']['HOST'] = '127.0.0.1'
DATABASES['default']['PORT'] = '5432'

# Dev cho phép truy cập
DEBUG = True
ALLOWED_HOSTS = ['*']

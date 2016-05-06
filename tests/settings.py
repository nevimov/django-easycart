EASYCART_CART_CLASS = 'tests.common.Cart'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

INSTALLED_APPS = [
    'django.contrib.sessions',
    'tests',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'easycart.urls'

SECRET_KEY = 'dummy-key'

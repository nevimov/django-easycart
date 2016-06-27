from os import path
from setuptools import setup, find_packages

if __name__ != '__main__':
    exit()

root_dir = path.abspath(path.dirname(__file__))

with open(path.join(root_dir, 'README.rst')) as readme_file:
    long_description = readme_file.read()

with open(path.join(root_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='django-easycart',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    version=version,
    license='MIT',
    description='A flexible session-based shopping cart for Django',
    long_description=long_description,
    author='nevimov',
    author_email='nevimov@gmail.com',
    url='https://github.com/nevimov/django-easycart',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='django shopping cart basket trolley',
)

from setuptools import setup, find_packages
import io
from os import path
import re


VERSION = re.search("VERSION = '([^']+)'", io.open(
    path.join(path.dirname(__file__), 'webencodings', '__init__.py'),
    encoding='utf-8'
).read().strip()).group(1)

LONG_DESCRIPTION = io.open(
    path.join(path.dirname(__file__), 'README.rst'),
    encoding='utf-8'
).read()


setup(
    name='webencodings',
    version=VERSION,
    url='https://github.com/SimonSapin/python-webencodings',
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    description='Character encoding aliases for legacy web content',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=find_packages(),
)

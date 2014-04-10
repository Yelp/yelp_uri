from setuptools import find_packages
from setuptools import setup

setup(
    name='yelp_uri',
    version='0.1.0',
    description="Uri utilities maintained by Yelp",
    author='Buck Golemon',
    platforms='all',
    classifiers=[
        'License :: Public Domain',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages('.', exclude=('tests*',)),
    install_requires=[
        'yelp_encodings',
        'yelp_bytes'
    ],
    dependency_links=[
        'https://github.com/Yelp/yelp_bytes/tarball/master#egg=yelp_bytes-0.1.0'
    ]
)

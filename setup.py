from setuptools import find_packages
from setuptools import setup


def main():
    setup(
        name='yelp_uri',
        version='1.1.0',
        description="Uri utilities maintained by Yelp",
        url='https://github.com/Yelp/yelp_uri',
        author='Buck Golemon',
        author_email='buck@yelp.com',
        platforms='all',
        classifiers=[
            'License :: Public Domain',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
        ],
        packages=find_packages('.', exclude=('tests*',)),
        install_requires=[
            'six',
            'yelp_encodings',
            'yelp_bytes'
        ],
    )

if __name__ == '__main__':
    exit(main())

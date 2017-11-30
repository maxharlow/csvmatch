from setuptools import setup
from .cli import __version__

setup(
    name='csvmatch',
    version=__version__,
    description='Find (fuzzy) matches between two CSV files in the terminal.',
    long_description=open('README.md').read(),
    author='Max Harlow',
    author_email='maxharlow@gmail.com',
    url='https://github.com/maxharlow/csvmatch',
    license='Apache',
    packages=[''],
    install_requires=[
        'chardet==3.0.4',
        'colorama==0.3.9',
        'unidecode==0.4.21',
        'dedupe==1.8.1',
        'jellyfish==0.5.6',
        'doublemetaphone==0.1'
    ],
    entry_points = {
        'console_scripts': [
            'csvmatch = cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities'
    ]
)

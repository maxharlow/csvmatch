from setuptools import setup

setup(
    name='csvmatch',
    version='1.23',
    description='Find (fuzzy) matches between two CSV files in the terminal.',
    long_description=open('README.md').read(),
    author='Max Harlow',
    author_email='contact@maxharlow.com',
    url='https://github.com/maxharlow/csvmatch',
    license='Apache',
    packages=[''],
    install_requires=[
        'chardet==5.1.0',
        'tqdm==4.64.1',
        'colorama==0.4.6',
        'unidecode==1.3.6',
        'dedupe==2.0.21',
        'jellyfish==0.9.0',
        'doublemetaphone==1.1'
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
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities'
    ]
)

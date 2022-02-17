from setuptools import setup

setup(
    name='csvmatch',
    version='1.21',
    description='Find (fuzzy) matches between two CSV files in the terminal.',
    long_description=open('README.md').read(),
    author='Max Harlow',
    author_email='contact@maxharlow.com',
    url='https://github.com/maxharlow/csvmatch',
    license='Apache',
    packages=[''],
    install_requires=[
        'chardet==4.0.0',
        'tqdm==4.62.3',
        'colorama==0.4.4',
        'unidecode==1.3.2',
        'dedupe==2.0.11',
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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities'
    ]
)

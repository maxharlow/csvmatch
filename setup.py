from setuptools import setup
import pip

# horrible hack to ensure dedupe installs correctly
pip.main(['install', 'numpy==1.10.1'])
pip.main(['install', 'dedupe==1.2.2'])

setup(
    name='csvmatch',
    version='1.7',
    description='Find (fuzzy) matches between two CSV files in the terminal.',
    long_description=open('README.md').read(),
    author='Max Harlow',
    author_email='maxharlow@gmail.com',
    url='https://github.com/maxharlow/csvmatch',
    license='Apache',
    packages=[''],
    install_requires=[
        'chardet==2.3.0',
        'colorama==0.3.5',
        'dedupe==1.2.2',
        'jellyfish==0.5.1',
        'metafone==0.5'
    ],
    entry_points = {
        'console_scripts': [
            'csvmatch = csvmatch:main'
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities'
    ]
)

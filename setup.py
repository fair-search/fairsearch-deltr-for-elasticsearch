from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fairsearchdeltres',
    version='1.0.1',
    description='A Python library to integrate DELTR with Learning To Rank (LTR) plugin in ElasticSearch',
    long_description=long_description,
    license='Apache 2.0',
    packages=['fairsearchdeltres'],
    author='Ivan Kitanovski',
    author_email='ivan.kitanovski@gmail.com',
    url='https://github.com/fair-search/fairsearchdeltr-elasticsearch-plugin',
    keywords=['search','fairness', 'deltr', 'disparate exposure in ranking', 'learning to rank'],
    python_requires=">=3.0",
    install_requires=[
        'pandas>=0.23',
        'scipy>=1.1.0',
        'fairsearchdeltr>=1.0.1'
    ],
    tests_require=[
        'pytest>=2.8.0'
    ],
    setup_requires=['pytest-runner'],
    test_suite="tests",
    classifiers=[
        'Development Status :: 4 - Beta', #'5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy'
      ]
)

# Fair search DELTR for ElasticSearch

[![image](https://img.shields.io/pypi/pyversions/fairsearchdeltr.svg)](https://pypi.org/project/fairsearchdeltr/)
[![image](https://img.shields.io/pypi/l/fairsearchdeltr.svg)](https://pypi.org/project/fairsearchdeltr/)

This is the Python library that serves as wrapper for the [DELTR](https://arxiv.org/pdf/1805.08716.pdf) model 
for fair ranking in [ElasticSearch](https://www.elastic.co/) with the [Learning to Rank plugin](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/).

## Requirements

This library requires:

- `Python 3.4+`
    - `Python` dependencies are stored in the `requirements.txt` file 
- `ElasticSearch` and _Learning to rank plugin_ (LTR) for `ElasticSearch`
    - Start a for supported version of `ElasticSarch` and follow the [installation steps](https://github.com/o19s/elasticsearch-learning-to-rank#installing)  

## Usage

There are several steps you need to take.

### Setup the features

Create the features you want to use in LTR. We have created sample features in 

### Index the data

### Train the model

### Search with the model

## Development

1. Clone this repository `git clone https://github.com/fair-search/fairsearch-deltr-for-elasticsearch`
2. Change directory to the directory where you cloned the repository `cd WHERE_ITS_DOWNLOADED/fairsearch-deltr-for-elasticsearch`
3. Use any IDE to work with the code

## Credits

The DELTR algorithm is described in this paper:

* Zehlike, Meike, and Carlos Castillo. "[Reducing Disparate Exposure in Ranking:
A Learning to Rank Approach](https://doi.org/10.1145/3132847.3132938)." arXiv preprint arXiv:1805.08716 (2018).

This library was developed by [Ivan Kitanovski](http://ivankitanovski.com/) based on the paper. See the [license](https://github.com/fair-search/fairsearch-deltr-for-elasticsearch/blob/master/LICENSE) file for more information.

## See also

You can also see the [DELTR Python library](https://github.com/fair-search/fairsearchdeltr-python)
 and [DELTR Java library](https://github.com/fair-search/fairsearchdeltr-java).
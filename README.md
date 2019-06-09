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
    - Start a supported version of `ElasticSarch` and follow the [installation steps](https://github.com/o19s/elasticsearch-learning-to-rank#installing)  

## Usage

There are several steps you need to take. In the following, we describe how to use the adapter to search on a collection of e-mails from W3C, included in /data/, which is one of the examples we used in the paper (see bibliography below).

### Index the training corpus

Index the training corpus. We have a sample data set in `zip` files `/data/candidates/candidates*.zip`.
Make sure to unzip them first. Then, you can index them with:

```bash
python deltr.py --index --document-dir ./data/candidates --index-name resumes
```

This will (re)index the `JSON` files under the folder `/data/candidates` in an index named `resumes`. 

Later, at any point, you can add the real documents over which you want to search using the trained ranking model. Those documents do not need to be in the same index, most commonly they will be in a different index.

### Setup the features

Create the features you want to use in LTR. We have created sample features in `/data/features.json`
Next, we need to upload these features to ElasticSearch.

```bash
python deltr.py --prepare --feature-set-file ./data/features.json --feature-set-name w3c
```

This will upload the features defined in `/data/features.json` in ElasticSearch under the name `w3c`.

### Train the model

After, we have defined and uploaded the features and indexed the data, we can now create a model to use for retrireval.
In order to build a DELTR model, we need to provide it with some training data. We have created a sample train set contained in two files:
 `/data/queries.csv` and `/data/judgements.csv`. You can run the model
 
```bash
python deltr.py --train --queries ./data/queries.csv --judgements ./data/judgements.csv --model deltr_vanilla --feature-set-name w3c
```

This is going to train a DELTR model (with default parameters) name `deltr_vanilla` using the questions in `/data/queries.csv` and 
judgements for those queries in `/data/judgements.csv`, with the features defined in the feature set name `w3c`

#### Debugging the model by observing the feature values

The library will use the features we defined in LTR to train the model. So, for debugging purposes, the library 
creates a `features.csv` file in the same folder where this is executed. There you can see what features were generated for each document.
It also creates a `model.txt` where you can see the final model, that was uploaded in LTR. 

*Note:* You can also specify tuning parameters from the command line as well. E.g.

```bash
python deltr.py --train --queries ./data/queries.csv --judgements ./data/judgements.csv --model deltr_not_vanilla --feature-set-name w3c --gamma 0.8
```

This will create a new model with the same files, only it will set the `gamma` parameter to 0.8. [Here](#options) you can see how to check all options.

### Search with the model

Once we have the model, we can start using to do some searches. 

```bash
python3 deltr.py --search --query html --model deltr_vanilla --index-name resumes
```

This will run a query with the keyword `html` using the model `deltr_vanilla` on the index `resumes`.

*Note:* You can also see a verbose output, which will contain the features calculated for each document returned.

```bash
python3 deltr.py --search --query html --model deltr_vanilla --index-name resumes --verbose
```

## <a name="options"></a> All options

Run the following command to get the full options list
```bash
python deltr.py --help
```

## Development

1. Clone this repository `git clone https://github.com/fair-search/fairsearch-deltr-for-elasticsearch`
2. Change directory to the directory where you cloned the repository `cd WHERE_ITS_DOWNLOADED/fairsearch-deltr-for-elasticsearch`
3. Use any IDE to work with the code

## Credits

The DELTR algorithm is described in this paper:

* Meike Zehlike, Gina-Theresa Diehn, Carlos Castillo. "[Reducing Disparate Exposure in Ranking:
A Learning to Rank Approach](https://doi.org/10.1145/3132847.3132938)." preprint arXiv:1805.08716 (2018).

This library was developed by [Ivan Kitanovski](http://ivankitanovski.com/) based on the paper. See the [license](https://github.com/fair-search/fairsearch-deltr-for-elasticsearch/blob/master/LICENSE) file for more information.

## See also

You can also see:
- [DELTR Python library](https://github.com/fair-search/fairsearch-deltr-python)
- [DELTR Java library](https://github.com/fair-search/fairsearch-deltr-java) 
- [Fair Search Elasticsearch plugin](https://github.com/fair-search/fairsearch-fair-for-elasticsearch)

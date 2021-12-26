[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
![Tests](https://github.com/jfuruness/lib_caida_collector/actions/workflows/tests.yml/badge.svg)

# lib\_caida\_collector
This package downloads relationship data from Caida's serial-2 dataset. It caches this information, and creates a BGP DAG from this.

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [Testing](#testing)
* [Development/Contributing](#developmentcontributing)
* [History](#history)
* [Credits](#credits)
* [Licence](#license)
* [TODO](#todo)

## Package Description

TODO

## Usage
* [lib\_caida\_collector](#lib_caida_collector)

From the command line, to download to /tmp/caida_collector.tsv:

```bash
lib_caida_collector
```

In a script:
TODO

## Installation
* [lib\_caida\_collector](#lib_caida_collector)

Install python and pip if you have not already. 

Make sure to upgrade pip with

```bash
pip3 install pip --upgrade
```

Then run:

```bash
pip3 install git@github.com:jfuruness/lib_caida_collector.git
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:
```bash
git clone https://github.com/jfuruness/lib_caida_collector.git
cd lib_caida_collector
pip3 install -e .[test]
```

To test the development package: [Testing](#testing)


## Testing
* [lib\_caida\_collector](#lib_caida_collector)

To test the package after installation:

```
cd lib_caida_collector
pytest lib_caida_collector
flake8 lib_caida_collector
mypy lib_caida_collector
```

If you want to run it across multiple environments, and have python 3.6-3.9 installed:

```
cd lib_caida_collector
tox
```


## Development/Contributing
* [lib\_caida\_collector](#lib_caida_collector)

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Run tox
6. Email me at jfuruness@gmail.com

## History
* [lib\_caida\_collector](#lib_caida_collector)
* 0.0.62 fixed bug where customers and providers where swapped
* 0.0.61 Fixed bug where BGPDAG was not returned
* 0.0.6 Fixed bug where file was not cached properly
* 0.0.5 First relatively stable version (still needs testing and a few other fixes)

## Credits
* [lib\_caida\_collector](#lib_caida_collector)

Thanks to Matt Jaccino and Tony Zheng, who helped with the original version of this located in lib_bgp_data

## License
* [lib\_caida\_collector](#lib_caida_collector)

BSD License (see license file)

## TODO
* [lib\_caida\_collector](#lib_caida_collector)

See Jira

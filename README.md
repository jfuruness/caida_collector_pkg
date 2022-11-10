[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
![Tests](https://github.com/jfuruness/caida_collector_pkg/actions/workflows/tests.yml/badge.svg)

# caida\_collector\_pkg
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
* [caida\_collector\_pkg](#caida_collector_pkg)

From the command line, to download to /tmp/caida_collector.tsv:

```bash
caida_collector_pkg
```

In a script:
TODO

## Installation
* [caida\_collector\_pkg](#caida_collector_pkg)

Install python and pip if you have not already.

Make sure to upgrade pip with

```bash
pip3 install pip --upgrade
```

Then run:

```bash
pip3 install git@github.com:jfuruness/caida_collector_pkg.git
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:
```bash
git clone https://github.com/jfuruness/caida_collector_pkg.git
cd caida_collector_pkg
pip3 install -e .[test]
```

To test the development package: [Testing](#testing)


## Testing
* [caida\_collector\_pkg](#caida_collector_pkg)

To test the package after installation:

```
cd caida_collector_pkg
pytest caida_collector_pkg
flake8 caida_collector_pkg
mypy caida_collector_pkg
```

If you want to run it across multiple environments, and have python 3.6-3.9 installed:

```
cd caida_collector_pkg
tox
```


## Development/Contributing
* [caida\_collector\_pkg](#caida_collector_pkg)

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Run tox
6. Email me at jfuruness@gmail.com

## History
* [caida\_collector\_pkg](#caida_collector_pkg)
* 0.1.2 Syntax fixes
* 0.1.1 Changed convience asn lists to be AS classes. Added ROV info
* 0.1.0 Changed the name, added Manifest.in, updated deps
* 0.0.63 Versioned up yamlable for Python3.10 compatability
* 0.0.62 fixed bug where customers and providers where swapped
* 0.0.61 Fixed bug where BGPDAG was not returned
* 0.0.6 Fixed bug where file was not cached properly
* 0.0.5 First relatively stable version (still needs testing and a few other fixes)

## Credits
* [caida\_collector\_pkg](#caida_collector_pkg)

Thanks to Matt Jaccino and Tony Zheng, who helped with the original version of this located in lib_bgp_data

## License
* [caida\_collector\_pkg](#caida_collector_pkg)

BSD License (see license file)

## TODO
* [caida\_collector\_pkg](#caida_collector_pkg)

See Jira

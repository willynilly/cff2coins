# cff2coins

Creates COinS tags from CFF files. Can be used to help Zotero cite your software and datasets.

[![PyPI - Version](https://img.shields.io/pypi/v/cff2coins.svg)](https://pypi.org/project/cff2coins)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cff2coins.svg)](https://pypi.org/project/cff2coins)

---

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contribution](#contribution)

## Installation

```console
pip install cff2coins
```

## Usage

This module allows software developers to generate COinS tags, which are HTML span tags containing citation metadata, from CFF files (e.g., CITATION.cff). They can embed these COinS tags into the views of their web applications so that their software and datasets are citable by citation managers, like Zotero. You can embed multiple COinS tag on a single page and then Zotero will read these tags and allow the user to select which items to import. This module uses the coins-parser module, which can also be used to dynamically create COinS tags for different resources in Python applications. 

#### Convert CFF to a COinS tag
```python
from cff2coins import CffCoinSpan
from pathlib import Path


# print COinS tag from CITATION.cff (e.g., your software or dataset) 
# if you add this span element to your HTML page, then Zotero can read it.
c: CffCoinSpan = CffCoinSpan.from_cff(cff_file_path = Path('CITATION.cff'))
print(c.to_html_string())
```
#### Convert CFF references to COinS tags
```python
# print COinS span elements for references in CITATION.cff (e.g., the software dependencies of your software). if you add these span elements to your HTML page, 
# then Zotero can read them and users can pick which resources they want to add to Zotero.

for r in c.references:
    # r is also a CffCoinSpan
    print(r.to_html_string())
```

#### Create COinS tags directly
You can also create a CffCoinSpan object directly from a list of tuples containing the metadata. CffCoinSpan uses the CoinSpan type from coins-parser. The CoinSpan is equivalent to list[tuple[str, str]]. 
```python
from cff2coins import CoinSpan
coin_span: CoinSpan = [
    ("url_ver", "Z39.88-2004"),
    ("ctx_ver", "Z39.88-2004"),
    ("rfr_id", "info:sid/zotero.org:2"),
    ("rft_val_fmt", "info:ofi/fmt:kev:mtx:dc"),
    ("rft.type", "computerProgram"),
    ("rft.title", "MyApp"),
    ("rft.publisher", "Some Company"),
    ("rft.description", "This is an example dummy software for testing."),
    ("rft.identifier", "https://zenodo.org/records/somenumber1"),
    ("rft.aufirst", "Willa"),
    ("rft.aulast", "Biley"),
    ("rft.au", "Willa Biley"),
    ("rft.au", "Wilò Rilü"),
    ("rft.au", "Jil van Hilo"),
    ("rft.date", "2025-04-15"),
]

cff_coin_span: CffCoinSpan = CffCoinSpan.from_coin_span(coin_span=coin_span)
```
#### Parse COinS tags from HTML 
You can use the CoinsParser class from the 
coins-parser module directly to parse COinS metadata 
from an html tag.

```python
from cff2coins import CoinsParser, CoinSpanList

# note that this returns a list of lists, 
# where each list is data for a coins span.
coin_spans: CoinSpanList = CoinsParser.parse(html)
for coin_span in coin_spans:
    cff_coin_span = CffCoinSpan.from_coin_span(coin_span=coin_span)
    print(cff_coin_span.to_html_string())

```
## License

`cff2coins` is distributed under the terms of the [Apache 2.0](https://spdx.org/licenses/Apache-2.0.html) license

## Contribution

Contributions in the form of feature requests, bug reports, bug fixes, tests, and feature implementations are welcome. To contribute code, please fork the project, and then do a pull request.

### Developer Notes

#### Building Locally

To build the tool locally, please follow the general advice from [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

```
python3 -m pip install --upgrade build
python3 -m build
```

#### Deploying

To deploy the tool, use the Github Action defined in .github/workflows/python-publish.yml
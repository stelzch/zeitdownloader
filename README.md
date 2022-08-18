# Die ZEIT Downloader

This is a simple downloader for the digital formats of the weekly newspaper [Die Zeit](https://www.zeit.de). A digital subscription is required.
It is written in 125 lines of python

[![asciicast Demo](https://asciinema.org/a/yUSupdGELwQc1KvLUlJmbXwch.svg)](https://asciinema.org/a/yUSupdGELwQc1KvLUlJmbXwch)



## Features

* Specify formats that are to be downloaded
* Skip redownload if file content matches (epub, mobi) or if file already exists (pdf) unless explicitly specified with `--reload`


## Installation

1. Clone this repo or download the `zeitdownload.py`.
2. Make sure the requirements are installed:
    * `sudo pip3 install -r requirements.txt`
3. Run with `./zeitdownload.py`.
4. To install globally, run `sudo python3 setup.py install`.

## Documentation

```
usage: zeitdownload.py [-h] --email EMAIL --password PASSWORD [--reload] [--pdf] [--epub]

Download "Die Zeit" in multiple formats from the premium subscription service

options:
  -h, --help           show this help message and exit
  --email EMAIL        Email you used for the digital subscription signup
  --password PASSWORD  Corresponding password
  --reload             Download file even though it already exists
  --pdf                Download full-page PDF
  --epub               Download EPUB file for E-Readers
```

# Die ZEIT Downloader

This is a simple downloader for the digital formats of the weekly newspaper [Die Zeit](https://www.zeit.de). A digital subscription is required.
It is written in only 70 lines of python

[![asciicast](https://asciinema.org/a/2Eg8PPKI47iFGxRYFP8Kigqz3.svg)](https://asciinema.org/a/2Eg8PPKI47iFGxRYFP8Kigqz3)

## Installation

1. Clone this repo or download the `zeitdownload.py`.
2. Make sure the requirements are installed:
    * `sudo pip3 install -r requirements.txt`
3. Run with `./zeitdownload.py`.

## Documentation

```
usage: zeitdownload.py [-h] --email EMAIL --password PASSWORD [--pdf] [--epub]
                       [--mobi]

Download "Die Zeit" in multiple formats from the premium subscription service

optional arguments:
  -h, --help           show this help message and exit
  --email EMAIL        Email you used for the digital subscription signup
  --password PASSWORD  Corresponding password
  --pdf                Download full-page PDF
  --epub               Download EPUB file for E-Readers
  --mobi               Download MOBI file for Kindles
```

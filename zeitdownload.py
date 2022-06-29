#!/usr/bin/env python3
import requests
import lxml.html
import cgi
import sys
import re
import os.path
import hashlib
from argparse import ArgumentParser

parser = ArgumentParser(description='Download "Die Zeit" in multiple formats from the premium subscription service')
parser.add_argument('--email', type=str, required=True,
        help='Email you used for the digital subscription signup')
parser.add_argument('--password', type=str, required=True,
        help='Corresponding password')
parser.add_argument('--reload', default=False, action='store_true',
        help='Download file even though it already exists')
parser.add_argument('--pdf', dest='formats',
        action='append_const', const='pdf',
        help='Download full-page PDF')
parser.add_argument('--epub', dest='formats',
        action='append_const', const='epub',
        help='Download EPUB file for E-Readers')
parser.add_argument('--mobi', dest='formats',
        action='append_const', const='mobi',
        help='Download MOBI file for Kindles')

args = parser.parse_args()

email = args.email
password = args.password
forcereload = args.reload
formats = args.formats

if formats == None:
    print("No formats specified, all done.")
    sys.exit(0)


# Src: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python#22058673
def md5sum(path):
    BUF_SIZE = 4 * 1024 * 1024 # 4 MiB
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

RELEASE_XPATH = '//p[@class="epaper-info-release-date"]'
DOWNLOAD_XPATH = "//a[contains(text(), '{}')]"
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"

s = requests.Session()
headers = {
        'Origin': 'https://meine.zeit.de',
}

login_page = s.get('https://meine.zeit.de/anmelden?url=https%3A%2F%2Fwww.zeit.de%2Findex&entry_service=sonstige')

response = s.post('https://meine.zeit.de/anmelden', {
    'entry_service': 'sonstige',
    'product_id': 'sonstige',
    'return_url': 'https://www.zeit.de/index',
    'email': email,
    'pass': password,
    'csrf_token': s.cookies['csrf_token']
}, headers=headers)

if not 'zeit_sso_201501' in s.cookies:
    print("Invalid login.")
    sys.exit(-1)

format_btns = {
    'pdf': 'GESAMT-PDF LADEN',
    'epub': 'EPUB FÜR E-READER LADEN',
    'mobi': 'MOBI FÜR KINDLE LADEN'
}

response = s.get('https://epaper.zeit.de/abo/diezeit')

document = lxml.html.fromstring(response.text)
release_dates = list(map(lambda el: el.text,
        document.xpath(RELEASE_XPATH)))
latest_release = release_dates[0]

if not re.match(DATE_REGEX, latest_release):
    print(f"Scraping broken, {latest_release} not valid date.")

response = s.get(f"https://epaper.zeit.de/abo/diezeit/{latest_release}")
document = lxml.html.fromstring(response.text)

for fmt in formats:
    link_elements = document.xpath(DOWNLOAD_XPATH.format(format_btns[fmt]))
    if len(link_elements) < 1:
        print(f"Skipping {fmt} download, scraping broken")
    link = link_elements[0].attrib['href']

    # Get filename from Content-Disposition header
    date = "-".join(latest_release.split(".")[::-1])
    filename = 'die_zeit_' + date + "." + fmt

    request_headers = {}
    if os.path.exists(filename) and not forcereload:
        # Somehow E-Tags do not work for PDF
        if fmt == 'pdf':
            print(f"File {filename} already exits. If you want to download anyway, use --reload")
            continue
        else:
            request_headers["If-None-Match"] = '"' + md5sum(filename) + '"'

    url = "https://epaper.zeit.de" + link \
            if not link.startswith('https') else link
    print(f"Downloading {fmt} from {url}...")
    response = s.get(url, headers=request_headers)

    if response.status_code == 304:
        print("  => Skipped, file did not change")
        continue

    if response.status_code != 200:
        print(f"Request for {url} returned status {response.status_code}", file=sys.stderr)
        sys.exit(-1)

    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded {fmt} to {filename}")

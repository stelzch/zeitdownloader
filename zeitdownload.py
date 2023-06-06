#!/usr/bin/env python3
import requests
import lxml.html
import sys
import re
import os.path
import hashlib
from argparse import ArgumentParser

RELEASE_XPATH = '//p[@class="epaper-info-release-date"]'
DOWNLOAD_XPATH = "//a[contains(text(), '{}')]"
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"

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
group = parser.add_mutually_exclusive_group()
group.add_argument('--date', type=str,
        help='Download file from specified date (dd.mm.yyyy)')
group.add_argument('--num-release', type=int, choices=range(0, 7),
        help='Download one of the past releases by numbers from the current one; \n \
        0 is the current release, 1 the previous one, up until 7')
args = parser.parse_args()

email = args.email
password = args.password
forcereload = args.reload
formats = args.formats
release_date = args.date
num_release = args.num_release

if release_date:
    if not re.match(DATE_REGEX, release_date):
        print(f"{release_date} is not a valid date.")
        sys.exit(5)

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

def download_file(format, filename, req_session, doc):
    link_elements = document.xpath(DOWNLOAD_XPATH.format(format_btns[fmt]))
    if len(link_elements) < 1:
        return -1
    link = link_elements[0].attrib['href']

    request_headers = {}
    if os.path.exists(filename) and not forcereload:
        # Somehow E-Tags do not work for PDF
        if fmt == 'pdf':
            return -2
        else:
            request_headers["If-None-Match"] = '"' + md5sum(filename) + '"'

    url = "https://epaper.zeit.de" + link \
            if not link.startswith('https') else link

    response = s.get(url, headers=request_headers)
    if response.status_code == 304:
        return 304
    if response.status_code != 200:
        return response
    return response.content


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
    'epub': 'EPUB FÜR E-READER LADEN'
}

# Figure out which date to use if no date was supplied directly
if not release_date:
    num = 0
    if num_release:
        num = num_release
    response = s.get('https://epaper.zeit.de/abo/diezeit')
    document = lxml.html.fromstring(response.text)
    latest_releases = list(map(lambda el: el.text,
                               document.xpath(RELEASE_XPATH)))
    if not re.match(DATE_REGEX, latest_releases[num]):
        print(f"Scraping broken, {latest_releases[num]} not valid date.")
    release_date = latest_releases[num]

# Get buttons for format downloads
# This is done separated from the download_file function to
# avoid an overhead through multiple downloads
response = s.get(f"https://epaper.zeit.de/abo/diezeit/{release_date}")
if (response.url == 'https://epaper.zeit.de/abo/diezeit'):
    print(f"No release published on {release_date}")
    sys.exit(6)
document = lxml.html.fromstring(response.text)

for fmt in formats:
    # Get filename from Content-Disposition header
    date = "-".join(release_date.split(".")[::-1])
    filename = 'die_zeit_' + release_date + "." + fmt
    
    print(f"Downloading {fmt}...")
    response = download_file(fmt, filename, s, document)
    if (response == -1):
        print(f"Skipping {fmt} download, scraping broken")
        continue
    elif (response == -2):
        print(f"File {filename} already exits. If you want to download anyway, use --reload")
        continue
    elif (response == 304):
        print(" => Skipped, file did not change")
        continue
    elif (isinstance(response, int)):
        print(f"Request returned status {response}", file=sys.stderr)
        continue

    # Everything is clear, function returns actual file
    with open(filename, 'wb') as file:
        file.write(response)
    print(f"Downloaded {fmt} to {filename}")

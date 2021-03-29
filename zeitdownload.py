#!/usr/bin/env python3
import requests
import lxml.html
import cgi
import sys
from argparse import ArgumentParser

parser = ArgumentParser(description='Download "Die Zeit" in multiple formats from the premium subscription service')
parser.add_argument('--email', type=str, required=True,
        help='Email you used for the digital subscription signup')
parser.add_argument('--password', type=str, required=True,
        help='Corresponding password')
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
formats = args.formats

if formats == None:
    print("No formats specified, all done.")
    sys.exit(0)

RELEASE_XPATH = '//p[@class="epaper-info-release-date"]'
DOWNLOAD_XPATH = "//a[contains(text(), '{}')]"

s = requests.Session()
response = s.post('https://meine.zeit.de/anmelden', {
    'entry_service': 'sonstige',
    'product_id': 'sonstige',
    'return_url': 'https://www.zeit.de/index',
    'email': email,
    'pass': password,
    'permanent': 'on'
})
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
response = s.get(f"https://epaper.zeit.de/abo/diezeit/{latest_release}")
document = lxml.html.fromstring(response.text)

for fmt in formats:
    link_elements = document.xpath(DOWNLOAD_XPATH.format(format_btns[fmt]))
    if len(link_elements) < 1:
        print(f"Skipping {fmt} download, scraping broken")
    link = link_elements[0].attrib['href']
    print(f"Downloading {fmt} from {link}...")
    response = s.get("https://epaper.zeit.de" + link 
            if not link.startswith('https') else link)

    # Get filename from Content-Disposition header
    filename = ''
    if 'Content-Disposition' in response.headers.keys():
        value, params = cgi.parse_header(response.headers['Content-Disposition'])
        filename = params['filename']
    else:
        filename = link.split('/')[-1]

    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded {fmt}.")

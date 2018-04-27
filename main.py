#!/usr/bin/env python3
import os
import sys
import time
import argparse
import datetime
import requests
import subprocess

from lxml import html
from twilio.rest import Client

required_env_vars = [
    'TWILIO_SID',
    'TWILIO_TOKEN'
]

for var in required_env_vars:
    if not var in os.environ:
        raise Exception('Twilio API credentials missing from environment')

TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']

def notify(title, text):
        os.system("""
        osascript -e 'display notification "{}" with title "{}"'
        """.format(text, title))

parser = argparse.ArgumentParser(
    description="Poll a given Resident Advisor URL and notify if resale tickets are available.",
)

parser.add_argument('url', help='Resident Advisor event page URL')
parser.add_argument('from_number', help='Phone number FROM which the text is sent (including country prefix)')
parser.add_argument('to_number', help='Phone number TO which the text is sent (including country prefix)')
parser.add_argument('-n', '--notify',
    help='Show a system notification when tickets are available',
    action='store_true')

args = parser.parse_args()

FROM_PHONE_NUMBER = args.from_number
PHONE_NUMBER = args.to_number

client = Client(TWILIO_SID, TWILIO_TOKEN)

text_sent = False

while True:
    response = requests.get(args.url)
    root = html.document_fromstring(response.content)

    tickets_with_resale = root.xpath('//li[@id="tickets"]/ul/li[@data-resale-tickets-available > 0]')

    if len(tickets_with_resale) > 0:
        print("%s: Tickets available" % (str(datetime.datetime.now())))

        if args.notify:
            notify("Tickets available", "")

        if not text_sent:
            message = client.messages.create(
                to=PHONE_NUMBER,
                from_=FROM_PHONE_NUMBER,
                body="Tickets available!",
            )
            text_sent = True

    time.sleep(10)

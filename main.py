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

def notify(title, text):
        os.system("""
        osascript -e 'display notification "{}" with title "{}"'
        """.format(text, title))

parser = argparse.ArgumentParser(
    description="Poll a given Resident Advisor URL and notify if resale tickets are available.",
)
parser.add_argument('url', help="Resident Advisor event page URL")
args = parser.parse_args()

TWILIO_SID = 'TWILIO_SID'
TWILIO_TOKEN = 'TWILIO_TOKEN'

FROM_PHONE_NUMBER = '+44'

PHONE_NUMBER = '+44'

client = Client(TWILIO_SID, TWILIO_TOKEN)

text_sent = False

while True:
    response = requests.get(args.url)
    root = html.document_fromstring(response.content)

    tickets_with_resale = root.xpath('//li[@id="tickets"]/ul/li[@data-resale-tickets-available > 0]')

    if len(tickets_with_resale) > 0:
        print("%s: Tickets available" % (str(datetime.datetime.now())))
        notify("Tickets available", "")

        if not text_sent:
            message = client.messages.create(
                to=PHONE_NUMBER,
                from_=FROM_PHONE_NUMBER,
                body="Tickets available!",
            )
            text_sent = True

    time.sleep(10)

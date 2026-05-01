import requests
import re
from lxml import html
import phonenumbers

def handler(request):
    url = request.args.get("url")

    if not url:
        return {
            "statusCode": 400,
            "body": {"error": "URL required"}
        }

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        tree = html.fromstring(res.content)

        # Extract visible text
        texts = tree.xpath('//body//*[not(self::script or self::style)]/text()')

        text_data = " ".join([t.strip() for t in texts if t.strip()])

        # Extract data
        emails = list(set(re.findall(
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            text_data
        )))

        phones = []
        for match in phonenumbers.PhoneNumberMatcher(text_data, "IN"):
            phones.append(
                phonenumbers.format_number(
                    match.number,
                    phonenumbers.PhoneNumberFormat.E164
                )
            )

        links = tree.xpath('//a/@href')

        return {
            "statusCode": 200,
            "body": {
                "emails": emails[:50],
                "phones": phones[:50],
                "links": links[:50]
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }

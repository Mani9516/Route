import requests
import phonenumbers
import re
from lxml import etree

def handler(request):
    url = request.args.get("url")

    if not url:
        return {
            "statusCode": 400,
            "body": {"error": "URL is required"}
        }

    try:
        response = requests.get(url)
        response.raise_for_status()

        parser = etree.HTMLParser()
        tree = etree.fromstring(response.content, parser)

        names = set()
        phone_numbers = set()
        email_addresses = set()

        for element in tree.xpath('//p | //li | //td'):
            text = ' '.join(element.itertext()).strip()

            # Name detection
            if re.match(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text):
                names.add(text)

            # Phone numbers
            for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
                phone_numbers.add(
                    phonenumbers.format_number(
                        match.number,
                        phonenumbers.PhoneNumberFormat.E164
                    )
                )

            # Emails
            email_match = re.search(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                text
            )
            if email_match:
                email_addresses.add(email_match.group())

        return {
            "statusCode": 200,
            "body": {
                "names": list(names),
                "phones": list(phone_numbers),
                "emails": list(email_addresses)
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }

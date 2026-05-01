import re
import requests
from lxml import html
from playwright.async_api import async_playwright
import phonenumbers

# ---------- FAST SCRAPER ----------
def fast_scrape(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    tree = html.fromstring(res.content)

    texts = tree.xpath('//body//*[not(self::script or self::style)]/text()')
    return " ".join([t.strip() for t in texts if t.strip()])


# ---------- PLAYWRIGHT SCRAPER ----------
async def browser_scrape(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        await browser.close()

        tree = html.fromstring(content)
        texts = tree.xpath('//body//*[not(self::script or self::style)]/text()')

        return " ".join([t.strip() for t in texts if t.strip()])


# ---------- AI DATA EXTRACTION ----------
def extract_data(text):
    data = {
        "emails": list(set(re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text))),
        "phones": [],
        "names": list(set(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text))),
        "urls": list(set(re.findall(r'https?://[^\s]+', text))),
        "prices": list(set(re.findall(r'₹\s?\d+(?:,\d+)*(?:\.\d+)?', text)))
    }

    # Phone extraction
    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        data["phones"].append(
            phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        )

    return data


# ---------- MAIN PIPELINE ----------
async def scrape_site(url):
    try:
        text = fast_scrape(url)

        # If too little data → fallback to browser
        if len(text) < 1000:
            text = await browser_scrape(url)

    except:
        text = await browser_scrape(url)

    return extract_data(text)

import asyncio
from scraper_engine import scrape_site

def handler(request):
    url = request.args.get("url")

    if not url:
        return {"statusCode": 400, "body": {"error": "URL required"}}

    try:
        data = asyncio.run(scrape_site(url))

        return {
            "statusCode": 200,
            "body": data
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }

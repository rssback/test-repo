import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime
import pytz

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://eksiseyler.com')
        await page.wait_for_selector('div.content-box')  # Adjust the selector based on actual site structure
        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        cards = soup.find_all("div", class_="content-box")

        card_data = []
        for card in cards:
            title_element = card.find("h2", class_="content-title")
            image_element = card.find("img")
            summary_element = card.find("p", class_="summary")
            link_element = card.find("a", href=True)
            timestamp_element = card.find("time")

            if title_element and image_element and summary_element and link_element and timestamp_element:
                card_info = {
                    "displaytitle": title_element.get_text(strip=True),
                    "image": image_element['src'] if image_element else '',
                    "summary": summary_element.get_text(strip=True),
                    "url": link_element['href'],
                    "timestamp": timestamp_element['datetime']
                }
                card_data.append(card_info)

        fg = FeedGenerator()
        fg.title('Ekşi Şeyler')
        fg.link(href='https://eksiseyler.com/', rel='alternate')
        fg.description('RSS Feeds')

        current_timestamp = datetime.datetime.now(pytz.utc)
        formatted_timestamp = current_timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')
        fg.pubDate(formatted_timestamp)

        for card in card_data:
            fe = fg.add_entry()
            fe.title(card['displaytitle'])
            fe.link(href=card['url'])
            fe.description(card['summary'])

            timestamp = datetime.datetime.fromisoformat(card['timestamp']).replace(tzinfo=pytz.utc)
            formatted_timestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')
            fe.pubDate(formatted_timestamp)

        fg.rss_file('rss/eksiseyler_feed.xml', extensions=True, pretty=True, encoding='UTF-8', xml_declaration=True)

asyncio.run(main())

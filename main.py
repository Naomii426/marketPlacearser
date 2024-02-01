import asyncio
import time

from playwright.async_api import async_playwright


class WbParser:

    def __init__(self):
        self.page = None
        self.context = None

    async def __page_down(self, page):
        time.sleep(3)
        await page.evaluate('''
                for (var i = 0; i < 25; i++) {
                    setTimeout(function() {
                    window.scrollBy(0, 500);
                    }, i * 300);
                }
        ''')

    async def __page_down_on_1000px(self, page):
        time.sleep(3)
        await page.evaluate('''
                   for (var i = 0; i <= 2; i++) {
                    setTimeout(function() {
                       window.scrollBy(0, 500);
                    }, i * 300);
                  }
        ''')

    async def __get_info(self, url: str):
        self.page2 = await self.context.new_page()
        await self.page2.goto(url=url)
        await self.__page_down_on_1000px(self.page2)

        name_of_product = await self.page2.locator(".product-page__title").text_content()
        price_of_product = await self.page2.inner_text(".price-block__wallet-price")
        if price_of_product is not None:
            print(name_of_product + " " + price_of_product)
        else:
            price_of_product = await self.page2.inner_text(".price-block__final-price")
            print(name_of_product + " " + price_of_product)

    async def __get_links(self):
        await self.page.wait_for_selector(".product-card-list")
        await self.__page_down(self.page)
        await self.page.wait_for_selector(f" :text('Покупателям')")
        time.sleep(15)
        search_result = await self.page.query_selector(".product-card-list")
        links = await search_result.query_selector_all(".product-card__link")
        for count, link in enumerate(links):
            if count > 200: break
            time.sleep(0.2)
            url = await link.get_attribute("href")
            await self.__get_info(url=url)

    async def parse(self):
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=False)
            self.context = await browser.new_context()
            self.page = await self.context.new_page()
            await self.page.goto("https://www.wildberries.ru/catalog/0/search.aspx?search=телефон")
            await self.__get_links()
            time.sleep(30)


async def main():
    await WbParser().parse()


asyncio.run(main())

import asyncio
import csv
import time
from class_struct import Items, Item
from class_url_struct import Url_Items, Url_Item
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError


class WbParser:

    def __init__(self):
        self.page = None
        self.context = None
        self.items = Items()
        self.urls = Url_Items()

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

    def __create_csv(self):
        with open('marketPlaces.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Наименование товара', 'Цена', 'Рейтинг', 'Ссылка', 'Продавец', 'Ссылка на продавца'])

    def __save_csv(self):
        with open('marketPlaces.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Наименование товара', 'Цена', 'Рейтинг', 'Ссылка', 'Продавец', 'Ссылка на продавца'])
            for product in self.items.products:
                writer.writerow([product.name, product.price, product.rating, product.url, product.name_of_seller,
                                 product.link_on_seller])

    async def __get_info(self, url: str):
        self.page2 = await self.context.new_page()
        await self.page2.goto(url=url)
        await self.__page_down_on_1000px(self.page2)
        try:
            name_of_product = await self.page2.locator(".product-page__title").text_content()
        except Exception:
            print("Наименование продукта не удалось загрузить")

        try:
            price_of_product = await self.page2.inner_text(".price-block__wallet-price", TimeoutError=1000)
        except Exception:
            price_of_product = await self.page2.inner_text(".price-block__final-price")

        try:
            rate_of_product = await self.page2.inner_text(".product-review__rating")
        except Exception:
            print("Не удалось получить рейтинг товара")

        try:
            name_of_seller = await self.page2.inner_text(".seller-info__name", TimeoutError=1000)
        except Exception:
            name_of_seller = await self.page2.inner_text(".seller-info__title")

        try:
            url_on_seller = await self.page2.query_selector(".seller-info__name")
            link_on_seller = "https://wildberries" + await url_on_seller.get_attribute("href")
        except Exception:
            link_on_seller = "https://www.wildberries"

        item = Item(url, name_of_product, price_of_product, rate_of_product, name_of_seller, link_on_seller)
        self.items.products.append(item)
        self.__save_csv()
        print(
            name_of_product + " " + price_of_product + " " + rate_of_product + " " + name_of_seller + " " + link_on_seller)
        await self.page2.close()

    async def __go_next_page(self):
        count = 5
        for i in range(count):
            await self.page.get_by_text("Следующая страница").click()
            await self.__page_down(self.page)
        await self.__get_links()

    async def __get_links(self):
        await self.page.wait_for_selector(".product-card-list")
        await self.__page_down(self.page)
        await self.page.wait_for_selector(f" :text('Покупателям')")
        time.sleep(15)
        self.search_result = await self.page.query_selector(".product-card-list")
        self.links = await self.search_result.query_selector_all(".product-card__link")
        await self.__get_url_of_product(self.links)

    async def __get_url_of_product(self, links):
        print(len(links))
        for count, link in enumerate(links):
            if count > 100000: break
            time.sleep(0.2)
            url = await link.get_attribute("href")
            await self.__get_info(url=url)

    async def parse(self):
        self.__create_csv()
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

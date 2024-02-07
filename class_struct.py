
class Item():
    def __init__(self, url: str, name: str, price: float, rating: float, name_of_seller: str, link_on_seller: str):
        self.url = url
        self.name = name
        self.price = price
        self.rating = rating
        self.name_of_seller = name_of_seller
        self.link_on_seller = link_on_seller
class Items():
    def __init__(self):
        self.products = []


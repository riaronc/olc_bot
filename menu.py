from aiogram import types
import keyboard as kb

MENU_TYPES = ["coffee", "drinks", "desserts", "food"]


class MenuItem:

    def __init__(self, id: int, name: str, price: int, img_link: str, menu_type: str):
        self.id = str(id)
        self.name = name
        self.price = price
        self.img_link = img_link
        self.type = menu_type


class Menu:
    coffee: [MenuItem]
    drinks: [MenuItem]
    desserts: [MenuItem]
    food: [MenuItem]
    menu = {}

    def create_menu(self, coffee_data, drinks_data, desserts_data, food_data):
        self.coffee = [MenuItem(id=item[0], name=item[1], price=item[2],
                                img_link=item[3], menu_type="coffee") for item in coffee_data]
        self.drinks = [MenuItem(id=item[0], name=item[1], price=item[2],
                                img_link=item[3], menu_type="drinks") for item in drinks_data]
        self.desserts = [MenuItem(id=item[0], name=item[1], price=item[2],
                                  img_link=item[3], menu_type="desserts") for item in desserts_data]
        self.food = [MenuItem(id=item[0], name=item[1], price=item[2],
                              img_link=item[3], menu_type="food") for item in food_data]
        self.menu = {
            "coffee": self.coffee,
            "drinks": self.drinks,
            "desserts": self.desserts,
            "food": self.food
        }

    def show_menu(self, query):
        possible_queries = MENU_TYPES
        if query.query in possible_queries:
            reply = [types.InlineQueryResultArticle(
                id=item.id,
                title=item.name,
                description=str(item.price) + " грн",
                input_message_content=types.InputMessageContent(
                    message_text=item.name,
                    entities=types.MessageEntity(type='text_link', url=item.img_link, offset=0, length=len(item.name))
                ),
                # url=item.img_link,
                # hide_url=False,
                thumb_url=str(item.img_link),
                thumb_height=48,
                thumb_width=48,
                reply_markup=kb.tools_menu
            ) for item in self.menu[query.query]]
            return reply

    def get_selected_item(self, menu_type: str, id: str):
        for item in self.menu[menu_type]:
            if item.id == id:
                return item

    def format_view_for_admin(self, menu_type: str):
        ret = ""
        for item in self.menu[menu_type]:
            ret += f"{item.id}. {item.name}, {item.price}$\n\n"
        return ret


class InlineMenuItem:

    def __init__(self, item: MenuItem, inline_id: str):
        self.item = item
        self.inline_id = inline_id

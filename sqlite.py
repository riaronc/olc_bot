import sqlite3
import json
from menu import Menu
from config import DEFAULT_IMG_LINK

class SQLite:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_menu(self, menu: Menu):
        with self.connection:
            coffee_data = self.cursor.execute("SELECT * FROM 'coffee'").fetchall()
            drinks_data = self.cursor.execute("SELECT * FROM 'drinks'").fetchall()
            desserts_data = self.cursor.execute("SELECT * FROM 'desserts'").fetchall()
            food_data = self.cursor.execute("SELECT * FROM 'food'").fetchall()
        menu.create_menu(coffee_data, drinks_data, desserts_data, food_data)

    def user_init(self, user_id, is_admin=0):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM 'users' WHERE user_id = ?", (user_id, )).fetchall()
            if not user:
                self.cursor.execute("INSERT INTO 'users' ('user_id', 'is_admin', 'cart', 'sum_to_pay')"
                                    "VALUES(?, ?, ?, ?)", (user_id, is_admin, '{"cart":[]}', 0))
            if user and is_admin == 42:
                self.cursor.execute("UPDATE 'users' SET is_admin = 42 WHERE user_id = ?", (user_id, ))
                self.connection.commit()

            # TODO add removing of existing admin

        return user

    def get_admins(self):
        with self.connection:
            admins = self.cursor.execute("SELECT user_id FROM 'users' WHERE is_admin = 42").fetchall()
        return admins

    def is_admin(self, user_id):
        with self.connection:
            admin = self.cursor.execute("SELECT is_admin FROM 'users' WHERE user_id = ?", (user_id, )).fetchall()
            print(admin[0])
        return admin[0][0]

    def add_to_cart(self, user_id, item):
        new_item = {
            "id": item.id,
            "type": item.type,
            "name": item.name,
            "price": item.price
        }

        with self.connection:
            cart_json = self.cursor.execute("SELECT * FROM 'users' WHERE user_id = ?", (user_id, )).fetchall()[0][3]
            cart_data = json.loads(cart_json)
            cart_list = cart_data["cart"]
            cart_list.append(new_item)
            cart_data["cart"] = cart_list
            cart_json = json.dumps(cart_data)
            self.cursor.execute("UPDATE 'users' SET cart = ? WHERE user_id = ?", (cart_json, user_id, ))
            self.connection.commit()

    def get_cart_items(self, user_id):
        with self.connection:
            cart_json = self.cursor.execute("SELECT * FROM 'users' WHERE user_id = ?", (user_id,)).fetchall()[0][3]
            cart_data = json.loads(cart_json)
            cart_list = cart_data["cart"]
        return cart_list

    def clear_cart(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE 'users' SET cart = ? WHERE user_id = ?", ('{"cart":[]}', user_id, ))
            self.connection.commit()

    def get_user_number(self, user_id):
        with self.connection:
            res = self.cursor.execute("SELECT phone_number FROM 'users' WHERE user_id = ?", (user_id, )).fetchall()
        if not res[0][0]:
            return 0
        else:
            return res[0][0]

    def update_phone_number(self, user_id, phone):
        if len(phone) == 10 and phone[0] == "0":
            phone = f"+38{phone}"
        elif len(phone) == 12 and phone[0] == "3":
            phone = f"+{phone}"
        with self.connection:
            self.cursor.execute("UPDATE 'users' SET phone_number = ? WHERE user_id = ?", (phone, user_id, ))
            self.connection.commit()

    # ADMIN FEATURES

    def change_price(self, table: str, id: int, new_price: int):
        with self.connection:
            if table == 'desserts':
                self.cursor.execute("UPDATE 'desserts' SET price = ? WHERE id = ?", (new_price, id, ))
                self.connection.commit()
            elif table == 'coffee':
                self.cursor.execute("UPDATE 'coffee' SET price = ? WHERE id = ?", (new_price, id, ))
                self.connection.commit()
            elif table == 'drinks':
                self.cursor.execute("UPDATE 'drinks' SET price = ? WHERE id = ?", (new_price, id, ))
                self.connection.commit()
            elif table == 'food':
                self.cursor.execute("UPDATE 'food' SET price = ? WHERE id = ?", (new_price, id, ))
                self.connection.commit()
            else:
                return 0
            return 1

    def add_item(self, table: str, name: str, price: int, img_link: str = DEFAULT_IMG_LINK):
        with self.connection:
            if table == 'desserts':
                self.cursor.execute("INSERT INTO 'desserts' ('name', 'price', 'photo_url')"
                                    "VALUES(?, ?, ?)", (name, price, img_link, ))
            elif table == 'coffee':
                self.cursor.execute("INSERT INTO 'coffee' ('name', 'price', 'photo_url')"
                                    "VALUES(?, ?, ?)", (name, price, img_link, ))
            elif table == 'drinks':
                self.cursor.execute("INSERT INTO 'drinks' ('name', 'price', 'photo_url')"
                                    "VALUES(?, ?, ?)", (name, price, img_link, ))
            elif table == 'food':
                self.cursor.execute("INSERT INTO 'food' ('name', 'price', 'photo_url')"
                                    "VALUES(?, ?, ?)", (name, price, img_link, ))
            else:
                return 0
            self.connection.commit()
            return 1

    def delete_item(self, table: str, item_id: int):
        with self.connection:
            if table == 'desserts':
                self.cursor.execute("DELETE FROM 'desserts' WHERE id = ?", (item_id, ))
            elif table == 'coffee':
                self.cursor.execute("DELETE FROM 'coffee' WHERE id = ?", (item_id, ))
            elif table == 'drinks':
                self.cursor.execute("DELETE FROM 'drinks' WHERE id = ?", (item_id, ))
            elif table == 'food':
                self.cursor.execute("DELETE FROM 'food' WHERE id = ?", (item_id, ))
            self.connection.commit()
        return 1

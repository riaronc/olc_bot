import json
import requests
from config import WFP_API
import text
import sqlite3
import hmac
import time
# MERCHANT_ACCOUNT = "t_me258"
# MERCHANT_DOMAIN_NAME = "https://t.me/onelovecoffee_bot"
MERCHANT_ACCOUNT = "freelance_user_5fbfad0800c3c"
MERCHANT_DOMAIN_NAME = "wayforpay.com/freelance"
TICKETS_DB = "db/tickets.db"
CHECK_STATUS_URL = "https://api.wayforpay.com/api"
PURCHASE_URL = "https://secure.wayforpay.com/pay"


class Ticket:
    user_id: int
    date: str
    ticket_id: str
    status = 0
    cart: str
    delivery_address: str

    def __init__(self, data):
        self.user_id = data


class WayForPay:

    def __init__(self):
        self.connection = sqlite3.connect(TICKETS_DB)
        self.cursor = self.connection.cursor()

    def create_ticket(self, user_id, cart, delivery_address):
        date = time.strftime("%d.%m.%y")
        with self.connection:
            id = len(self.cursor.execute("SELECT * FROM 'tickets'").fetchall())
        ticket_id = f"pre-kek{id}"
        sum_to_pay = 0
        for item in cart:
            sum_to_pay += item["price"]
        if sum_to_pay != 0:
            with self.connection:
                self.cursor.execute("INSERT INTO 'tickets' ('user_id', 'date', 'ticket_id', 'status', 'cart', \
                'additional') VALUES(?, ?, ?, 0, ?, ?)", (user_id, date, ticket_id, str(cart), delivery_address))
                self.connection.commit()
            message = self.generate_link(sum_to_pay, ticket_id)
            return message
        else:
            return text.CART_CANNOT_BE_EMPTY

    @staticmethod
    def generate_link(amount, order_reference):
        data = {
            'merchantAccount': MERCHANT_ACCOUNT,
            'merchantDomainName': MERCHANT_DOMAIN_NAME,
            'orderReference': order_reference,
            'orderDate': str(int(time.time())),
            'amount': str(amount),
            'currency': 'UAH',
            'productName[]': 'ONE LOVE',
            'productCount[]': '1',
            'productPrice[]': str(amount),
        }
        decoded = ""
        for i in data:
            decoded += data[i]
            decoded += ";"
        decoded = decoded[:-1]
        data['merchantSignature'] = hmac.new(str.encode(WFP_API), str.encode(decoded), digestmod='md5').hexdigest()
        decoded = requests.post(url=PURCHASE_URL, data=data).content.decode('utf-8')
        num = decoded.find('data-vkh=')
        test = decoded[num + 10:num + 46]
        link = "🎫 посилання для оплати: \n\n" + 'https://secure.wayforpay.com/page?vkh=' + test + \
               "\n\n\n⚠️ замовлення буде зібрано після успішної оплати"
        message = {
            "order_reference": order_reference,
            "link": link
        }
        return message

    @staticmethod
    def check_ticket_status(order_reference):
        check_data = {
            'transactionType': 'CHECK_STATUS',
            'merchantAccount': MERCHANT_ACCOUNT,
            'orderReference': order_reference,
            'merchantSignature': '',
            'apiVersion': 1
        }
        props = f"{MERCHANT_ACCOUNT};{order_reference}"
        check_data["merchantSignature"] = hmac.new(str.encode(WFP_API), str.encode(props), digestmod='md5').hexdigest()
        ret = requests.post(url=CHECK_STATUS_URL, data=json.dumps(check_data)).content.decode('utf-8')
        answer = json.loads(ret)
        if answer["transactionStatus"] == 'Approved':
            status = text.SUCCESSFUL_PAYMENT
        else:
            status = text.FAILED_PAYMENT
        return status

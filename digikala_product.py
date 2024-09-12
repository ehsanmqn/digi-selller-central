import requests
import re
from PIL import Image
from io import BytesIO


class DigikalaProduct:
    def __init__(self, product_id):
        self.product_id = product_id
        self.api_url = f'https://sandbox.diginext.ir/api/v3/product-creation/be-seller/{self.product_id}'
        self.edit_api_url = f'https://sandbox.diginext.ir/api/v3/product-edit/{self.product_id}'
        self.product_data = {}
        self.edit_data = {}
        self.headers = {
            "accept": "application/json",
            "x-response-code": "200"
        }

    def fetch_product_data(self):
        response = requests.get(self.api_url, headers=self.headers)
        if response.status_code == 200:
            self.product_data = response.json().get('data', {})
        else:
            raise Exception(f"Failed to retrieve data, status code: {response.status_code}")

    def fetch_product_edit_data(self):
        response = requests.get(self.edit_api_url, headers=self.headers)
        if response.status_code == 200:
            self.edit_data = response.json().get('data', {})
        else:
            raise Exception(f"Failed to retrieve edit data, status code: {response.status_code}")

    def extract_product_info(self):
        if not self.product_data:
            return None

        product_info = {
            "status": "ok",
            "name": self.product_data.get("name"),
            "brand": self.product_data.get("brand"),
            "productId": self.product_data.get("productId"),
            "canSell": self.product_data.get("commission", {}).get("canSell"),
            "commission": self.product_data.get("commission", {}).get("commission"),
            "productURL": self.product_data.get("productURL"),
            "referencePrice": self.product_data.get("referencePrice"),
            "productImage": self.product_data.get("productImage"),
            "fulfillmentAndDeliveryCost": {
                "factor": self.product_data.get("fulfillmentAndDeliveryCost", {}).get("factor"),
                "minimum_cost": self.product_data.get("fulfillmentAndDeliveryCost", {}).get("minimum_cost"),
                "maximum_cost": self.product_data.get("fulfillmentAndDeliveryCost", {}).get("maximum_cost"),
            },
            "category": {
                "id": self.product_data.get("category", {}).get("id"),
                "title": self.product_data.get("category", {}).get("title"),
                "theme": self.product_data.get("category", {}).get("theme"),
            },
            "site": self.product_data.get("site"),
            "product_dimension": {
                "width": self.product_data.get("product_dimension", {}).get("width"),
                "length": self.product_data.get("product_dimension", {}).get("length"),
                "height": self.product_data.get("product_dimension", {}).get("height"),
                "weight": self.product_data.get("product_dimension", {}).get("weight"),
            },
            "price_type": self.product_data.get("price_type"),
        }

        return product_info

    def extract_edit_info(self):
        if not self.edit_data:
            return None

        edit_info = {
            "status": self.edit_data.get("status"),
            "product_data": self.edit_data.get("product_data", {}),
            "moderation_response": self.edit_data.get("moderation_response", {}),
            "steps_moderation_status": self.edit_data.get("steps_moderation_status", {}),
            "locked_for_moderation": self.edit_data.get("locked_for_moderation"),
            "multi_seller_product": self.edit_data.get("multi_seller_product"),
            "edit_status": self.edit_data.get("edit_status"),
        }

        return edit_info

    def contains_symbols_or_emojis(self, text):
        # Define patterns for symbols and emojis
        symbol_pattern = re.compile(r'[^\w\s]', re.UNICODE)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)

        has_symbols = bool(symbol_pattern.search(text))
        has_emojis = bool(emoji_pattern.search(text))

        return has_symbols or has_emojis

    def is_white_background(self):
        if "productImage" not in self.product_data:
            return False

        image_url = self.product_data["productImage"]

        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            image = image.convert("RGB")

            # Define white color range (you can adjust the tolerance if needed)
            white_color = (255, 255, 255)
            tolerance = 10

            # Check if all corners of the image are white
            width, height = image.size
            corners = [
                (0, 0),  # Top-left
                (width - 1, 0),  # Top-right
                (0, height - 1),  # Bottom-left
                (width - 1, height - 1)  # Bottom-right
            ]

            for corner in corners:
                r, g, b = image.getpixel(corner)
                if not (abs(r - white_color[0]) <= tolerance and
                        abs(g - white_color[1]) <= tolerance and
                        abs(b - white_color[2]) <= tolerance):
                    return False

            return True

        except Exception as e:
            print(f"An error occurred while checking the image: {e}")
            return False

    def is_title_length_valid(self):
        product_info = self.extract_product_info()
        if product_info and "name" in product_info:
            title = product_info["name"]
            if len(title) >= 60:
                return True
            else:
                return False
        else:
            return False

    def is_image_size_valid(self):
        if "productImage" not in self.product_data:
            return False

        image_url = self.product_data["productImage"]

        try:
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))

            # Check image dimensions
            width, height = image.size
            if width >= 1000 and height >= 1000:
                return True
            else:
                return False

        except Exception as e:
            return False

    def has_seven_or_more_images(self):
        if self.product_data and 'images' in self.product_data:
            return len(self.product_data['images']) >= 7
        return False

    def has_video_content(self):
        if self.product_data and 'videos' in self.product_data and self.product_data['videos']:
            return True
        return False

    def has_long_description(self):
        description = self.product_data.get('description', '')
        return len(description) >= 1000

    def has_at_least_five_attributes(self):
        attributes = self.product_data.get('attributes', {})
        attribute_count = sum(len(v) for v in attributes.values())
        return attribute_count >= 5

    def check_emojies(self):
        product_info = self.extract_product_info()
        if product_info and "name" in product_info:
            title = product_info["name"]
            if self.contains_symbols_or_emojis(title):
                return False
            else:
                return True
        else:
            return None

# Example usage
# product_id = 'dkp-16587276'
# product = DigikalaProduct(product_id)
# product.fetch_product_data()
# product.fetch_product_edit_data()
# product.check_title()
# product.is_white_background()
# product.is_title_length_valid()
# product.is_image_size_valid()
# product.extract_edit_info()
#
# if product.has_seven_or_more_images():
#     print("The product has 7 or more images.")
# else:
#     print("The product has fewer than 7 images.")
#
# if product.has_video_content():
#     print("The product includes video content.")
# else:
#     print("The product does not include video content.")
#
# if product.has_long_description():
#     print("The product description includes 1000 or more characters.")
# else:
#     print("The product description does not include 1000 or more characters.")
#
# if product.has_at_least_five_attributes():
#     print("The product has at least 5 attributes.")
# else:
#     print("The product has fewer than 5 attributes.")

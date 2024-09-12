import requests

class DigikalaSalesReport:
    def __init__(self, api_url, headers=None):
        self.api_url = api_url
        self.headers = headers if headers else {
            "accept": "application/json",
            "x-response-code": "200"
        }
        self.data = {}

    @staticmethod
    def extract_image_url(url):
        end_pos = url.find('.jpg') + len('.jpg')
        return url[:end_pos]

    def fetch_sales_report(self):
        response = requests.get(self.api_url, headers=self.headers)
        if response.status_code == 200:
            self.data = response.json().get('data', {})
        else:
            raise Exception(f"Failed to retrieve data, status code: {response.status_code}")

    def get_average_conversion_rate(self):
        items = self.data.get('items', [[]])[0]
        total_conversion_rate = sum(item.get('conversion_rate', 0) for item in items)
        return total_conversion_rate / len(items) if items else 0

    def suggest_campaigns(self):
        average_conversion_rate = self.get_average_conversion_rate()
        high_conversion_products = []

        items = self.data.get('items', [[]])[0]
        for item in items:
            if item.get('conversion_rate', 0) > average_conversion_rate:
                high_conversion_products.append({
                    "product_id": item['product_id'],
                    "title": item['title'],
                    "image": self.extract_image_url(item['image']),
                    "conversion_rate": item['conversion_rate'],
                    "avg_conversion_rate": average_conversion_rate,
                    "suggested_campaign": f"Campaign for {item['title']}"
                })

        return high_conversion_products
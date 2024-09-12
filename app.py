from flask import Flask, jsonify
from flask_cors import CORS

from digikala_order_history import DigikalaOrderHistory
from digikala_inventory import DigikalaInventory
from sale_insight import DigikalaSalesReport
from digikala_product import DigikalaProduct
from seller_products import SellerProducts

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def extract_image_url(url):
    end_pos = url.find('.jpg') + len('.jpg')
    return url[:end_pos]


@app.route('/api/products', methods=['GET'])
def get_product_list():
    seller_product = SellerProducts(None)  # Initialize with no specific ID for listing
    seller_products = seller_product.get_and_parse_products()

    inventory = DigikalaInventory()
    products_with_stock = inventory.extract_product_ids_from_stock()

    return jsonify({"products": seller_products})


@app.route('/api/high-sales-products-not-in-stock', methods=['GET'])
def get_products_not_in_stock():
    # Fetch products with stock data
    inventory = DigikalaInventory()
    inventory.fetch_inventory_data()
    products_with_stock = inventory.extract_product_ids_from_stock()
    print("Products with warehouse stock >= 0: ", products_with_stock)

    # Fetch all products
    seller_product = SellerProducts()  # Initialize SellerProduct
    all_products = seller_product.get_and_parse_products()  # Get the list of all products
    print("All products: ", all_products)

    # Identify products not in stock
    products_not_in_stock = [product for product in all_products if product['product_id'] not in products_with_stock]
    print("Products not in stock: ", products_not_in_stock)

    # Fetch high sales products
    order_history = DigikalaOrderHistory()
    high_sales_products = order_history.get_high_sales_products()

    # Filter products not in stock to include only those in high sales
    high_sales_not_in_stock = [product for product in products_not_in_stock if product['product_id'] in high_sales_products]
    print("High sales products not in stock: ", high_sales_not_in_stock)

    return jsonify({
        "products": high_sales_not_in_stock
    })


@app.route('/api/product/<product_id>', methods=['GET'])
def get_product_info(product_id):
    product = DigikalaProduct(product_id)
    product.fetch_product_data()
    product.fetch_product_edit_data()
    product_info = product.extract_product_info()

    # Collecting the information
    seo_info = {
        'title_emoji': product.check_emojies(),
        'title_length_valid': product.is_title_length_valid(),
        'white_background': product.is_white_background(),
        'image_size_valid': product.is_image_size_valid(),
        'seven_or_more_images': product.has_seven_or_more_images(),
        'video_content': product.has_video_content(),
        'long_description': product.has_long_description(),
        'at_least_five_attributes': product.has_at_least_five_attributes(),
        'main_image_link': extract_image_url(product_info.get('productImage', 'Not available')),
        'product_title': product_info.get('name', 'Not available')
    }

    # Competitor analysis
    competitor_analysis = {
        "Sales": {
            "product_id": product_id,
            "value": 76953,
            "top_5_competitors_avg": 52907
        },
        "Revenue": {
            "product_id": product_id,
            "value": 768760.47,
            "top_5_competitors_avg": 531363.81
        },
        "Price": {
            "product_id": product_id,
            "value": 9.99,
            "top_5_competitors_avg": 10.97
        },
        "BSR": {
            "product_id": product_id,
            "value": 106,
            "top_5_competitors_avg": 1283
        },
        "Number of Reviews": {
            "product_id": product_id,
            "value": 2250,
            "top_5_competitors_avg": 43525
        },
        "Rating": {
            "product_id": product_id,
            "value": 4.4,
            "top_5_competitors_avg": 4.5
        }
    }
    seo_info['competitor_analysis'] = competitor_analysis

    # Keyword analysis
    top_keyword_analysis = {
        "total-keywords": 5451,
        "top-10-keywords": 877,
        "total-search-volume": 6491241,
        "top-10-search-volume": 1905035
    }

    seo_info['top_keyword_analysis'] = top_keyword_analysis

    # Calculate score and percentage
    boolean_checks = [v for v in seo_info.values() if isinstance(v, bool)]
    total_checks = len(boolean_checks)
    score = sum(1 for value in boolean_checks if value)
    score_percent = (score / total_checks) * 100 if total_checks > 0 else 0

    # Add the score and percentage to the result
    seo_info['score'] = score
    seo_info['score_percent'] = score_percent

    return jsonify(seo_info)


@app.route('/api/campaign-recommendation', methods=['GET'])
def get_sales_report():
    api_url = "https://sandbox.diginext.ir/api/v3/insight/sales-reports?range=last_7_days"
    sales_report = DigikalaSalesReport(api_url)
    sales_report.fetch_sales_report()

    high_conversion_campaigns = sales_report.suggest_campaigns()
    return jsonify({"campaign_suggestions": high_conversion_campaigns})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(debug=True)

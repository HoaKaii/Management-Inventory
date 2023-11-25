from datetime import datetime

class Product:
    def __init__(self, code, name, selling_price, purchase_price, quantity, production_date, expiration_date):
        self.code = code
        self.name = name
        self.selling_price = selling_price
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.production_date = datetime.strptime(production_date, '%Y-%m-%d')
        self.expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')

class Invoice:
    def __init__(self, invoice_code, invoice_date):
        self.invoice_code = invoice_code
        self.invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d')
        self.product_list = []

class ManageProduct:
    def __init__(self):
        self.product_list = []
        self.invoice_list = []

    def add_product(self, product):
        existing_product = None
        for p in self.product_list:
            if p.code == product.code:
                existing_product = p
                break

        if existing_product:
            # Mã sản phẩm đã tồn tại trong danh sách sản phẩm của quản lý,
            existing_product.quantity += product.quantity
            existing_product.selling_price = product.selling_price
            existing_product.purchase_price = product.purchase_price
            existing_product.production_date = product.production_date
            existing_product.expiration_date = product.expiration_date
            print(f"Products with the code {product.code} already exist in the list. Information has been updated.")
        else:
            # Mã sản phẩm chưa tồn tại trong danh sách sản phẩm của quản lý,
            self.product_list.append(product)
            print("The product has been added successfully.")

    def search_product(self, keyword):
        if keyword is None:
            return self.product_list
        elif not keyword:
            raise ValueError("Keyword cannot be empty.")
        else:
            results = []
            for product in self.product_list:
                if keyword.lower() in product.name.lower():
                    results.append(product)
            return results

    def display_product_list(self):
        if not self.product_list:
            print("No products available.")
            return
        print("\nProduct List:")
        print("{:<10} {:<20} {:<10} {:<10} {:<10} {:<15} {:<15}".format(
            "Code", "Name", "Selling Price", "Purchase Price", "Quantity", "Production Date", "Expiration Date"))
        print("-" * 90)
        for product in self.product_list:
            print("{:<10} {:<20} {:<10} {:<10} {:<10} {:<15} {:<15}".format(
                product.code, product.name, product.selling_price, product.purchase_price,
                product.quantity, product.production_date.strftime('%Y-%m-%d'), product.expiration_date.strftime('%Y-%m-%d')))

    def calculate_revenue_by_product(self, date):
        if not isinstance(date, datetime):
            raise ValueError("Invalid date format.")
        revenue_by_product = {}
        for invoice in self.invoice_list:
            if invoice.invoice_date.date() == date.date():
                for item in invoice.product_list:
                    code = item['product_code']
                    revenue = item['total_price']
                    if code in revenue_by_product:
                        revenue_by_product[code] += revenue
                    else:
                        revenue_by_product[code] = revenue
        return revenue_by_product

    def calculate_revenue_by_store(self, month, year):
        if not (isinstance(month, int) and isinstance(year, int)):
            raise ValueError("Invalid month or year format.")
        revenue_by_store = {}
        for invoice in self.invoice_list:
            if invoice.invoice_date.month == month and invoice.invoice_date.year == year:
                for item in invoice.product_list:
                    code = item['product_code']
                    revenue = item['total_price']
                    if code in revenue_by_store:
                        revenue_by_store[code] += revenue
                    else:
                        revenue_by_store[code] = revenue
        return revenue_by_store

    def sort_revenue(self, ascending=True):
        revenue_by_store = self.calculate_revenue_by_store(datetime.now().month, datetime.now().year)
        sorted_revenue = sorted(revenue_by_store.items(), key=lambda x: x[1], reverse=not ascending)
        return sorted_revenue

    def display_top_bottom_products(self, top=True, count=5):
        sorted_revenue = self.sort_revenue(top)
        if not sorted_revenue:
            print("No data available.")
            return
        if top:
            print("\nTop {} Products:".format(count))
        else:
            print("\nBottom {} Products:".format(count))

        print("{:<10} {:<20} {:<15}".format("Code", "Name", "Total Revenue"))
        print("-" * 45)
        for i in range(min(count, len(sorted_revenue))):
            code, revenue = sorted_revenue[i]
            product = None
            for p in self.product_list:
                if p.code == code:
                    product = p
                    break
            if product is not None:
                print("{:<10} {:<20} {:<15}".format(code, product.name, revenue))

    def update_price_for_near_expiration(self):
        for product in self.product_list:
            expiration_date = product.expiration_date
            current_date = datetime.now()
            days_to_expire = (expiration_date - current_date).days

            if days_to_expire == 21:
                product.selling_price *= 0.765  # 23.5% discount
            elif days_to_expire < 21:
                product.selling_price *= 0.431  # 56.9% discount

    def update_product_info(self, code, new_info):
        if not new_info or not isinstance(new_info, dict):
            raise ValueError("Invalid new information format.")
        product = None
        for p in self.product_list:
            if p.code == code:
                product = p
                break
        if product:
            for key, value in new_info.items():
                if hasattr(product, key):
                    setattr(product, key, value)
                else:
                    raise ValueError(f"The {key} attribute does not exist in the Product class")
            print("Product information updated successfully.")
        else:
            print("Product not found.")

    def delete_product(self, code):
        product = None
        for p in self.product_list:
            if p.code == code:
                product = p
                break
        if product:
            self.product_list.remove(product)
            print("Product deleted successfully.")
        else:
            print("Product not found.")

    def add_invoice(self, invoice):
        try:
            self.validate_invoice(invoice)
            self.invoice_list.append(invoice)
            # Giảm số lượng sản phẩm tương ứng trong danh sách sản phẩm chính thức
            for item in invoice.product_list:
                product_code = item['product_code']
                quantity_sold = item['quantity_sold']
                product = None
                for p in self.product_list:
                    if p.code == product_code:
                        product = p
                        break
                if product:
                    product.quantity -= quantity_sold
                else:
                    raise ValueError(f"The product with the code {product_code} can't be found in the product list.")

            print("The invoice is added successfully.")
        except ValueError as e:
            print(f"Error adding invoice: {e}")

    def validate_invoice(self, invoice):
        if not isinstance(invoice, Invoice):
            raise ValueError("Invalid invoice instance.")
        for product_code, quantity in invoice.products.items():
            self.validate_product(product_code, quantity)

    def validate_product(self, product_code, quantity):
        product = None
        for p in self.product_list:
            if p.code == product_code:
                product = p
                break
        if quantity <= 0:
            raise ValueError("Invalid quantity. Quantity must be greater than 0.")
        if product is None:
            raise ValueError(f"The product with the code {product_code} can't be found in the product list.")
        if quantity > product.quantity:
            raise ValueError(
                f"Insufficient quantity for product {product_code}. Available quantity: {product.quantity}.")


from .database import SessionLocal
from .models import Product

def seed_products():
    db = SessionLocal()

    if db.query(Product).count() == 0:
        products = [
            Product(product_id="P101", name="Laptop", available_stock=10, unit_price=50000, tax_percentage=18),
            Product(product_id="P102", name="Mouse", available_stock=50, unit_price=500, tax_percentage=12),
            Product(product_id="P103", name="Keyboard", available_stock=30, unit_price=1500, tax_percentage=12),
        ]

        db.add_all(products)
        db.commit()

    db.close()
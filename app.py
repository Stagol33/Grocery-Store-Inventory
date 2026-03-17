from sqlalchemy import (create_engine, Column, Integer, 
                        String, Date, ForeignKey, func)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import csv
import datetime
import os

# 1. Database Setup
Base = declarative_base()
engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# 2. Models
class Brand(Base):
    __tablename__ = 'brands'
    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String, unique=True)
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, unique=True)
    product_quantity = Column(Integer)
    product_price = Column(Integer)  # Stored in cents
    date_updated = Column(Date)
    brand_id = Column(Integer, ForeignKey('brands.brand_id'))
    brand = relationship("Brand", back_populates="products")

# 3. Data Cleaning & Validation Functions
def clean_price(price_str):
    """Converts '$3.19' or '3.19' to 319 (int)"""
    try:
        clean_str = price_str.replace('$', '').strip()
        return int(float(clean_str) * 100)
    except ValueError:
        return None

def clean_date(date_str):
    """Converts '11/1/2018' to Date object"""
    try:
        return datetime.datetime.strptime(date_str, '%m/%d/%Y').date()
    except ValueError:
        return None

def clean_quantity(quant_str):
    """Ensures quantity is a positive integer"""
    try:
        val = int(quant_str)
        return val if val >= 0 else None
    except ValueError:
        return None

# 4. CSV Import Logic
def add_csv_data():
    # Import Brands
    if os.path.exists('brands.csv'):
        with open('brands.csv', newline='') as f:
            data = csv.reader(f)
            next(data)  # Skip header
            for row in data:
                brand_exists = session.query(Brand).filter(Brand.brand_name == row[0]).one_or_none()
                if not brand_exists:
                    new_brand = Brand(brand_name=row[0])
                    session.add(new_brand)
        session.commit()

    # Import Inventory
    if os.path.exists('inventory.csv'):
        with open('inventory.csv', newline='') as f:
            data = csv.reader(f)
            next(data)
            for row in data:
                name = row[0]
                price = clean_price(row[1])
                quantity = int(row[2])
                date = clean_date(row[3])
                brand_name = row[4]
                
                brand = session.query(Brand).filter(Brand.brand_name == brand_name).first()
                
                # Logic for Exceeds: Update if newer, ignore if older
                existing_product = session.query(Product).filter(Product.product_name == name).one_or_none()
                if existing_product:
                    if date >= existing_product.date_updated:
                        existing_product.product_price = price
                        existing_product.product_quantity = quantity
                        existing_product.date_updated = date
                        existing_product.brand_id = brand.brand_id if brand else None
                else:
                    new_product = Product(
                        product_name=name,
                        product_price=price,
                        product_quantity=quantity,
                        date_updated=date,
                        brand_id=brand.brand_id if brand else None
                    )
                    session.add(new_product)
        session.commit()

# 5. Menu Logic Functions
def view_product():
    while True:
        id_input = input("\nEnter Product ID to view: ")
        product = session.query(Product).filter(Product.product_id == id_input).one_or_none()
        
        if product:
            print(f"\nID: {product.product_id} | {product.product_name}")
            print(f"Brand: {product.brand.brand_name if product.brand else 'No Brand'}")
            print(f"Price: ${product.product_price / 100:.2f} | Quantity: {product.product_quantity}")
            print(f"Updated: {product.date_updated}")
            
            # Extra Credit: Edit or Delete
            sub_choice = input("\nWould you like to (E)dit, (D)elete, or (R)eturn to main menu? ").upper()
            if sub_choice == 'E':
                edit_product(product)
                break
            elif sub_choice == 'D':
                session.delete(product)
                session.commit()
                print("Product deleted successfully.")
                break
            else:
                break
        else:
            print("That ID does not exist. Please try again.")

def edit_product(product):
    print(f"Editing {product.product_name}. Leave blank to keep current value.")
    
    new_name = input(f"New Name [{product.product_name}]: ")
    if new_name: product.product_name = new_name
    
    new_price = input(f"New Price (ex: 4.50) [${product.product_price/100:.2f}]: ")
    if new_price: product.product_price = clean_price(new_price)
    
    new_qty = input(f"New Quantity [{product.product_quantity}]: ")
    if new_qty: product.product_quantity = clean_quantity(new_qty)
    
    product.date_updated = datetime.date.today()
    session.commit()
    print("Product updated!")

def add_new_product():
    name = input("Product Name: ")
    quantity = clean_quantity(input("Quantity: "))
    price = clean_price(input("Price (ex: 5.99): "))
    brand_name = input("Brand Name: ")
    
    brand = session.query(Brand).filter(Brand.brand_name == brand_name).first()
    if not brand:
        brand = Brand(brand_name=brand_name)
        session.add(brand)
        session.commit()

    # Exceeds Logic: Update existing if same name
    existing = session.query(Product).filter(Product.product_name == name).one_or_none()
    if existing:
        print("Product already exists. Updating record...")
        existing.product_quantity = quantity
        existing.product_price = price
        existing.date_updated = datetime.date.today()
        existing.brand_id = brand.brand_id
    else:
        new_prod = Product(
            product_name=name, product_quantity=quantity,
            product_price=price, date_updated=datetime.date.today(),
            brand_id=brand.brand_id
        )
        session.add(new_prod)
    session.commit()
    print("Record saved!")

def run_analysis():
    print("\n--- INVENTORY ANALYSIS ---")
    most_exp = session.query(Product).order_by(Product.product_price.desc()).first()
    least_exp = session.query(Product).order_by(Product.product_price.asc()).first()
    
    # Advanced Analysis (Exceeds)
    total_items = session.query(func.sum(Product.product_quantity)).scalar()
    avg_price = session.query(func.avg(Product.product_price)).scalar()
    
    print(f"Most Expensive: {most_exp.product_name} (${most_exp.product_price/100:.2f})")
    print(f"Least Expensive: {least_exp.product_name} (${least_exp.product_price/100:.2f})")
    print(f"Total Inventory Quantity: {total_items}")
    print(f"Average Product Price: ${avg_price/100:.2f}")

def backup_database():
    with open('backup.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['product_name', 'product_price', 'product_quantity', 'date_updated', 'brand_name'])
        for p in session.query(Product).all():
            writer.writerow([
                p.product_name, 
                f"${p.product_price/100:.2f}", 
                p.product_quantity, 
                p.date_updated.strftime('%m/%d/%Y'), 
                p.brand.brand_name if p.brand else ''
            ])
    print("Backup successful! File saved as 'backup.csv'.")

def menu():
    while True:
        print("\n(V) View Product | (N) Add Product | (A) Analysis | (B) Backup | (E) Exit")
        choice = input("Select an option: ").upper()
        
        if choice == 'V': view_product()
        elif choice == 'N': add_new_product()
        elif choice == 'A': run_analysis()
        elif choice == 'B': backup_database()
        elif choice == 'E': 
            print("Goodbye!")
            break
        else:
            print("Invalid input. Please choose V, N, A, B, or E.")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv_data()
    menu()
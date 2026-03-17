# Grocery Store Inventory Management System

A Python-based command-line application that manages a grocery store's inventory using **SQLAlchemy ORM** and a **SQLite** database. This tool allows users to import data from CSV files, analyze stock levels, add new products, and create backups.

## 🚀 Features

- **Automated Data Import:** Cleans and imports `brands.csv` and `inventory.csv` into a relational database.
- **Data Normalization:** Converts prices to integers (cents) to avoid floating-point errors and handles date string-to-object conversion.
- **Intelligent Duplicate Handling:** During import, if a duplicate product name is found, the system only saves the record with the most recent `date_updated`.
- **Interactive Menu:**
  - **View Product (V):** Look up items by ID. View details including the Brand Name (via ORM relationships). Includes options to **Edit** or **Delete** the record.
  - **Add Product (N):** Add new items with automated brand lookup/creation and duplicate name protection.
  - **Analysis (A):** View insights such as the most/least expensive items, total stock quantity, and average pricing.
  - **Backup (B):** Export the current state of the database to a standardized `backup.csv`.

## 🛠️ Tech Stack

- **Language:** Python 3.13
- **Database:** SQLite
- **ORM:** SQLAlchemy 2.0+
- **Environment:** Virtualenv

## 📦 Installation & Setup

1. **Clone the repository:**

````bash
git clone git@github.com:Stagol33/Grocery-Store-Inventory.git
cd Grocery-Store-Inventory
    ```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv env
source env/bin/activate # On Windows: .\env\Scripts\activate
````

3. **Install dependencies:**

```bash
pip install sqlalchemy
```

4. **Prepare Data Files:**
   Ensure brands.csv and inventory.csv are in the root directory.

5. **Run the Application:**

```bash
python app.py
```

📂 Project Structure
app.py: Main application logic, database models, and menu system.

brands.csv: Initial brand data.

inventory.csv: Initial product inventory data.

.gitignore: Configured to exclude env/, **pycache**, and local .db files.

requirements.txt: List of Python dependencies.

📋 Extra Credit Requirements Met
Duplicate Prevention: Implemented logic to check for existing products and only keep the most recent update.

Edit/Delete Functionality: Users can modify or remove records directly from the "View Product" menu.

Relationship Mapping: The app displays human-readable Brand Names instead of Foreign Key IDs by utilizing SQLAlchemy relationships.

Advanced Analysis: Includes total inventory count and average product pricing.

Formatted Backup: The backup.csv includes headers and matches the original source format exactly.

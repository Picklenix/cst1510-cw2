import sqlite3

def clear_cart_table():
    try:
        conn = sqlite3.connect("new_shopping_system.db")
        cursor = conn.cursor()

        # Delete all rows from the Cart table
        cursor.execute("DELETE FROM Cart")

        conn.commit()
        print("All items have been removed from the Cart table.")
    except sqlite3.Error as e:
        print(f"Error clearing Cart table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_cart_table()

'''import sqlite3

def view_products():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("new_shopping_system.db")
        cursor = conn.cursor()

        # Execute a query to select all products
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()

        # Check if there are any products
        if not products:
            print("No products available.")
            return

        # Print the header
        print("\nID | Product Name                     | Price   | Stock")
        print("---------------------------------------------------------")

        # Print each product in a formatted way
        for row in products:
            product_id, product_name, price, stock = row
            print(f"{product_id:<3} | {product_name:<30} | ${price:<7} | {stock}")

    except sqlite3.Error as e:
        print(f"Error retrieving products: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_products()'''
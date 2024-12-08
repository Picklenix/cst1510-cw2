import sqlite3

def create_database():
    try:
        # Connect to the database (it will be created if it doesn't exist)
        conn = sqlite3.connect("new_shopping_system.db")
        cursor = conn.cursor()

        # Create Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL CHECK (stock >= 0)
            );
        ''')

        # Clear existing data in Products table (optional)
        cursor.execute("DELETE FROM Products")

        # Insert sample data into Products table
        sample_products = [
            ("New Python Programming eBook", 12.99, 150),
            ("New Photo Editing License", 35.99, 70),
            ("New Study Playlist MP3", 7.99, 250),
            ("New Gamification Course", 59.99, 40),
            ("New Game Development Course", 45.99, 30)
        ]
        
        cursor.executemany("INSERT INTO Products (product_name, price, stock) VALUES (?, ?, ?)", sample_products)

        conn.commit()
        print("Database created and sample data inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
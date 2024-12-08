import socket
import threading
import sqlite3

class NewServer:
    def __init__(self):
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.PORT = 5000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER, self.PORT))
        print("[INFO] New Server initialized.")

    def get_product_list(self):
        try:
            conn = sqlite3.connect("new_shopping_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Products")
            products = cursor.fetchall()
            conn.close()

            if not products:
                return "No products available."
            
            return "\n".join(f"{row[0]}|{row[1]}|{row[2]}|{row[3]}" for row in products)
        except sqlite3.Error as e:
            print(f"Error getting product list: {e}")
            return "Error retrieving product list"

    def add_to_cart(self, product_id, quantity):
        try:
            conn = sqlite3.connect("new_shopping_system.db")
            cursor = conn.cursor()

            cursor.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                return "Product not found"
            
            available_stock = product[0]
            if available_stock < quantity:
                return "Insufficient stock"
            
            cursor.execute("INSERT INTO Cart (productID, quantity) VALUES (?, ?)", (product_id, quantity))
            conn.commit()
            conn.close()
            
            return f"Product ID {product_id} added to cart successfully."
           
        except sqlite3.Error as e:
            print(f"Error adding to cart: {e}")
            return "Error adding product to cart"

    def view_cart(self):
        try:
            conn = sqlite3.connect("new_shopping_system.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Products.id, Products.product_name, Cart.quantity, Products.price 
                FROM Cart 
                JOIN Products ON Cart.productID = Products.id
            """)

            cart_items = cursor.fetchall()

            conn.close()

            if not cart_items:
                return "Cart is empty."

            return "\n".join(f"{row[0]}|{row[1]}|{row[2]}|${row[3]:.2f}" for row in cart_items)
        except sqlite3.Error as e:
            print(f"Error viewing cart: {e}")
            return "Error retrieving cart items"

    def process_checkout(self, cart_data):
        try:
            conn = sqlite3.connect("new_shopping_system.db")
            cursor = conn.cursor()

            items = cart_data.split(";")

            for item in items:
                product_id, quantity = map(int, item.split(","))

                cursor.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
                product = cursor.fetchone()

                if not product:
                    return f"Product ID {product_id} does not exist."

                available_stock = product[0]
                if available_stock < quantity:
                    return f"Insufficient stock for Product ID {product_id}."

                # Update stock in Products table
                cursor.execute("UPDATE Products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
                
                # Remove from Cart based on productID
                cursor.execute("DELETE FROM Cart WHERE productID = ?", (product_id,))
                
            conn.commit()
            conn.close()

            return "Checkout successful"
        except sqlite3.Error as e:
            print(f"Error processing checkout: {e}")
            return "Error processing checkout"

    def remove_from_cart(self, product_id, quantity):
        try:
            conn = sqlite3.connect("new_shopping_system.db")
            cursor = conn.cursor()

            cursor.execute("SELECT quantity FROM Cart WHERE productID = ?", (product_id,))
            cart_item = cursor.fetchone()

            if not cart_item:
                return "Product not found in cart."

            current_quantity = cart_item[0]
            if current_quantity < quantity:
                return "Insufficient quantity in cart."

            if current_quantity == quantity:
                cursor.execute("DELETE FROM Cart WHERE productID = ?", (product_id,))
            else:
                cursor.execute("UPDATE Cart SET quantity = quantity - ? WHERE productID = ?", (quantity, product_id))

            conn.commit()
            conn.close()

            return f"Product ID {product_id} removed from cart successfully."
        except sqlite3.Error as e:
            print(f"Error removing from cart: {e}")
            return "Error removing product from cart"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                print(f"[{addr}] Disconnected.")
                break

            print(f"[{addr}] Received message: {msg.strip()}")

            if msg.strip().upper() == "VIEW":
                response = server.get_product_list()

            elif msg.startswith("CHECKOUT:"):
                cart_data = msg.split("CHECKOUT:", 1)[1]
                response = server.process_checkout(cart_data)

            elif msg.startswith("ADD_TO_CART:"):
                _, product_id, quantity = msg.split(":")
                response = server.add_to_cart(int(product_id), int(quantity))

            elif msg.startswith("REMOVE_FROM_CART:"):
                _, product_id, quantity = msg.split(":")
                response = server.remove_from_cart(int(product_id), int(quantity))

            elif msg == "VIEW_CART":
                response = server.view_cart()

            else:
                response = "Invalid command"

            conn.send(response.encode('utf-8'))
        except sqlite3.Error as e:
            print(f"Error handling client {addr}: {e}")
    conn.close()

def start_server():
    global server
    server = NewServer()  
    server.server_socket.listen()
    print(f"[LISTENING] New Server is listening on {server.SERVER}:{server.PORT}")

    while True:
        conn, addr = server.server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
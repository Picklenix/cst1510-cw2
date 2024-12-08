import sys
import socket
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QInputDialog, QMessageBox, QTextEdit, QLineEdit, QListWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class NewClient:
    def __init__(self):
        self.cart = {}
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.PORT = 5000  
        self.client_socket = None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.SERVER, self.PORT))
            print(f"Connected to server at {self.SERVER}:{self.PORT}")
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def send_message(self, message):
        try:
            self.client_socket.send(message.encode('utf-8'))
            response = self.client_socket.recv(4096).decode('utf-8')
            return response
        except Exception as e:
            print(f"Error communicating with server: {e}")
            return None

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            print("Disconnected from server")

    def view_product(self):
        response = self.send_message('VIEW')
        return response if response else "No products available."

    def add_to_cart(self, product_id, quantity):
        response = self.send_message(f"ADD_TO_CART:{product_id}:{quantity}")
        if "successfully" in response.lower():
            if product_id in self.cart:
                self.cart[product_id] += quantity
            else:
                self.cart[product_id] = quantity
        return response

    def view_cart(self):
        response = self.send_message("VIEW_CART")
        if response and response != "Cart is empty.":
            self.cart.clear()
            for line in response.split("\n"):
                if line.strip():
                    parts = line.split("|")
                    if len(parts) == 4:
                        cart_product_id, _, quantity, _ = map(str.strip, parts)
                        self.cart[cart_product_id] = int(quantity)
        return response

    def delete_item(self, item_id):
        if item_id in self.cart:
            quantity = self.cart[item_id]
            response = self.send_message(f"REMOVE_FROM_CART:{item_id}:{quantity}")
            if "successfully removed" in response.lower():
                del self.cart[item_id]
            return response
        return "Item not in cart."

    def confirm_purchase(self):
        if not self.cart:
            return "The cart is empty. Nothing to purchase."
        cart_data = ";".join([f"{item},{quantity}" for item, quantity in self.cart.items()])
        response = self.send_message(f'CHECKOUT:{cart_data}')
        if response and "Error" not in response:
            self.cart.clear()
        return response

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = NewClient()
        
        self.setWindowTitle("NIX VENDING MACHINE")
        self.setGeometry(200, 110, 800, 600)
        
        main_layout = QHBoxLayout()
        
        # Left panel for buttons
        left_panel = QVBoxLayout()
        
        heading_label = QLabel("NIX VENDING MACHINE", alignment=Qt.AlignmentFlag.AlignCenter)
        heading_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        heading_label.setStyleSheet("color: #4CAF50;")
        
        left_panel.addWidget(heading_label)

        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 18px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """

        self.view_products_button = QPushButton("VIEW PRODUCTS")
        self.add_to_cart_button = QPushButton("ADD TO CART")
        self.view_cart_button = QPushButton("VIEW CART")
        self.checkout_button = QPushButton("CHECKOUT")

        for button in [self.view_products_button, self.add_to_cart_button, self.view_cart_button, self.checkout_button]:
            button.setStyleSheet(button_style)
            left_panel.addWidget(button)

        left_panel.addStretch()

        # Right panel for displaying content
        right_panel = QVBoxLayout()
        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setFont(QFont("Arial", 12))
        right_panel.addWidget(self.content_area)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect button clicks to their respective functions
        self.view_products_button.clicked.connect(self.show_products)
        self.add_to_cart_button.clicked.connect(self.add_to_cart)
        self.view_cart_button.clicked.connect(self.view_cart)
        self.checkout_button.clicked.connect(self.checkout)

    def show_products(self):
        if not self.client.connect():
            QMessageBox.critical(self, "Connection Error", "Failed to connect to server.")
            return
        
        products = self.client.view_product()
        self.content_area.setPlainText(products)

    def add_to_cart(self):
        product_id, ok1 = QInputDialog.getText(self, "Add to Cart", "Enter Product ID:")
        if ok1 and product_id:
            quantity_text, ok2 = QInputDialog.getText(self, "Add to Cart", "Enter Quantity:")
            if ok2 and quantity_text.isdigit():
                quantity = int(quantity_text)
                response = self.client.add_to_cart(product_id.strip(), quantity)
                QMessageBox.information(self, "Add to Cart", response)

    def view_cart(self):
        cart_contents = self.client.view_cart()
        if cart_contents:
            self.content_area.setPlainText(cart_contents)
        else:
            self.content_area.setPlainText("Your cart is empty.")

    def checkout(self):
        while True:
            choice, ok = QInputDialog.getItem(self, "Checkout", 
                "Choose an action:", 
                ["View Cart", "Add Items", "Delete Items", "Confirm Purchase", "Cancel"], 
                0, False)
            
            if not ok or choice == "Cancel":
                break

            if choice == "View Cart":
                self.view_cart()
            elif choice == "Add Items":
                self.add_to_cart()
            elif choice == "Delete Items":
                self.delete_item()
            elif choice == "Confirm Purchase":
                if self.confirm_purchase():
                    break

    def delete_item(self):
        item_id, ok = QInputDialog.getText(self, "Delete Item", "Enter the product ID to delete:")
        if ok and item_id:
            if item_id in self.client.cart:
                quantity = self.client.cart[item_id]
                confirm = QMessageBox.question(self, "Confirm Deletion", 
                    f"Are you sure you want to remove {quantity} of product ID {item_id} from the cart?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if confirm == QMessageBox.StandardButton.Yes:
                    response = self.client.delete_item(item_id)
                    QMessageBox.information(self, "Delete Item", response)
            else:
                QMessageBox.warning(self, "Error", f"Product ID {item_id} is not in the cart.")

    def confirm_purchase(self):
        if not self.client.cart:
            QMessageBox.information(self, "Checkout", "The cart is empty. Nothing to purchase.")
            return False
        else:
            confirm = QMessageBox.question(self, "Confirm Purchase", 
                "Are you sure you want to confirm your purchase?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                response = self.client.confirm_purchase()
                QMessageBox.information(self, "Checkout Result", response)
                return "Error" not in response
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
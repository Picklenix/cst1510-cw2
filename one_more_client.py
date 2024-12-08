import socket

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
        if response:
            print("\nAvailable Products:")
            print("ID | Product Name                     | Price   | Stock")
            print("---------------------------------------------------------")
            
            for line in response.split("\n"):
                if line.strip():  
                    parts = line.split("|")
                    if len(parts) == 4:  
                        product_id, name, price, stock = map(str.strip, parts)
                        print(f"{product_id:<3} | {name:<30} | ${price:<7} | {stock}")

    def add_to_cart(self):
        self.view_product()  
        product_id = input("Enter the product ID to add to cart: ").strip()
        
        try:
            quantity_input = input("Enter quantity: ")
            quantity = int(quantity_input)

            if quantity > 0:
                response = self.send_message(f"ADD_TO_CART:{product_id}:{quantity}")
                print(f"Server response: {response}")

                if "successfully" in response.lower():
                    # Store the product ID directly from user input
                    if product_id in self.cart:
                        self.cart[product_id] += quantity  
                    else:
                        self.cart[product_id] = quantity  
                    print(f"Successfully added {quantity} of product ID {product_id} to your cart.")
                else:
                    print(response)  

            else:
                print("Invalid quantity. Please enter a positive number.")

        except ValueError: 
            print("Invalid input. Please enter a valid number.")

    def view_cart(self):
        response = self.send_message("VIEW_CART")
        
        if response == "Cart is empty." or not response.strip():
            print("The cart is empty.")
        
        else:
            # Clear local cart before displaying contents
            self.cart.clear()
            
            print("\nYour Cart:")
            print("Product ID | Product Name                     | Quantity | Price   | Total")
            print("---------------------------------------------------------------")

            for line in response.split("\n"):
                if line.strip():  
                    parts = line.split("|")
                    if len(parts) == 4:  
                        cart_product_id, name, quantity, price = map(str.strip, parts)
                        total_price = float(price.replace('$', '').strip()) * int(quantity)
                        print(f"{cart_product_id:<11} | {name:<30} | {quantity:<8} | ${price:<7} | ${total_price:.2f}")
                        
                        # Update local cart dictionary with correct IDs
                        # Ensure we use the original IDs from the server
                        self.cart[cart_product_id] = int(quantity)

    def delete_item(self):
        item_id = input("Enter the product ID to delete: ").strip()
        
        if item_id in self.cart:
            quantity = self.cart[item_id]
            confirm = input(f"Are you sure you want to remove {quantity} of product ID {item_id} from the cart? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Optionally, allow the user to specify a quantity to remove
                # remove_quantity = input(f"Enter quantity to remove (1-{quantity}): ").strip()
                # if remove_quantity.isdigit() and 1 <= int(remove_quantity) <= quantity:
                #     remove_quantity = int(remove_quantity)
                # else:
                #     print("Invalid quantity. Removing the entire quantity.")
                #     remove_quantity = quantity
                
                response = self.send_message(f"REMOVE_FROM_CART:{item_id}:{quantity}")
                
                if response is None:
                    print("No response from server. Please try again.")
                elif "successfully removed" in response.lower():  # Adjust this based on your server's response
                    del self.cart[item_id]
                    print(f"Product ID {item_id} has been removed from the cart.")
                else:
                    print(f"Failed to remove item: {response}")
            else:
                print("Deletion canceled.")
        else:
            print(f"Product ID {item_id} is not in the cart.")
    def checkout(self):
        while True:
            self.view_cart()
            choice = input('''Enter 1 to add items to cart
Enter 2 to delete items from cart
Enter 3 to confirm your purchase
Your choice: ''')

            if choice == '1':
                self.add_to_cart()
            elif choice == '2':
                self.delete_item()
            elif choice == '3':
                if self.confirm_purchase():
                    break
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

    def confirm_purchase(self):
        if not self.cart:
            print("The cart is empty. Nothing to purchase.")
            return False
        else:
            # Prepare data for checkout using original IDs from local cart
            cart_data = ";".join([f"{item},{quantity}" for item, quantity in self.cart.items()])
            
            response = self.send_message(f'CHECKOUT:{cart_data}')
            
            if response:
                print(response)
                
                if "Error" not in response:
                    for item, quantity in self.cart.items():
                        print(f"Product ID: {item}, Quantity: {quantity}")
                    # Clear local cart after successful purchase
                    self.cart.clear()
                    return True
                else:
                    print("Checkout failed. Your cart remains unchanged.")
                    return False
            else:
                print("No response from server. Please try again.")
                return False

if __name__ == "__main__":
    client = NewClient()

    if client.connect():
        while True:
            command = input("Enter command (view/add/cart/checkout/quit): ")
            if command.lower() == 'view':
                client.view_product() 
            elif command.lower() == 'add':
                client.add_to_cart() 
            elif command.lower() == 'cart':
                client.view_cart() 
            elif command.lower() == 'checkout':
                client.checkout() 
            elif command.lower() == 'quit':
                break 
            else:
                print("Invalid command")
    client.disconnect()

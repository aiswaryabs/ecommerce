from store.models import Product, Category, Profile

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None  # Assign user if authenticated
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}  # Initialize a new cart if none exists
        self.cart = cart


    def add(self, product, quantity):
      product_id = str(product.id)
      if product_id in self.cart:
        self.cart[product_id]['quantity'] += quantity
      else:
        self.cart[product_id] = {
            'quantity': quantity,
            'price': str(product.price),
        }
      print("Cart after adding:", self.cart)  # Debugging
      self.session.modified = True


    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products

    def get_quants(self):
        quantities = {product_id: item['quantity'] for product_id, item in self.cart.items()}
        return quantities

    def update(self, product, quantity):
      product_id = str(product)
      if product_id in self.cart:
        # Update the quantity while preserving other details (e.g., price)
        self.cart[product_id]['quantity'] = quantity
        self.session.modified = True
    def delete(self,product):
        product_id=str(product)
        #delete 
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified=True

    def cart_total(self):
    # Get product IDs from the cart
      product_ids = self.cart.keys()
      products = Product.objects.filter(id__in=product_ids)  # Fetch products from the database
    
      total = 0  # Start the total at 0

      for product in products:
        product_id = str(product.id)  # Convert the product ID to a string to match cart keys
        if product_id in self.cart:
            details = self.cart[product_id]  # Get the product details (price and quantity)
            price = product.price  # Product price (Decimal)
            quantity = details.get('quantity', 0)  # Quantity from cart (integer)
            if product.is_sale:
                total+=product.sale_price * quantity
            else  :  
                total += price * quantity  # Calculate the total for this product

      return total
            

    def _load_cart(self):
      """Load the cart data from the user's profile."""
      if self.user:  # Check if the user is authenticated
        try:
            profile = self.user.profile
            self.cart = profile.cart_data or {}  # Load cart data or initialize as empty
            self.session['cart'] = self.cart  # Update session cart
            print("Cart loaded (updated):", self.cart)  # Debugging
        except Profile.DoesNotExist:
            print("Profile does not exist for user")
      else:
        self.cart = self.session.get('cart', {})

    def _save_cart(self):
      """Save the cart data back to the user's profile."""
      if self.session.get('cart'):  # Ensure there is data in the session cart
        if self.user:  # Check if the user is authenticated
            try:
                profile = self.user.profile
                profile.cart_data = self.cart
                profile.save()
                print("Cart saved (updated):", self.cart)  # Debugging
            except Profile.DoesNotExist:
                print("Profile does not exist for user")
      else:
        print("No cart data to save")

    def clear(self):
        """Clear the cart and save the session."""
        self.cart = {}
        self.session['cart'] = self.cart
        self.session.modified = True
        print("Cart cleared")  # Debugging     


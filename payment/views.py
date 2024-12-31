from django.shortcuts import render,redirect, get_object_or_404
from cart.cart import Cart
from payment.models import ShippingAddress,Order,OrderItem
from  django.contrib.auth.models import User
from payment.forms import ShippingForm,PaymentForm
from django.contrib import messages
from store.models import Product,Profile
import datetime

# Create your views here.


def payment_success(request):

    return render(request, "payment_success.html",{})


from django.shortcuts import render

from .forms import ShippingForm
from .models import ShippingAddress

def checkout(request): 
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()  # Correctly call the method

    if request.user.is_authenticated:
        # Checkout as logged-in user
        try:
            # Get or create a ShippingAddress for the logged-in user
            shipping_user_profile, created = ShippingAddress.objects.get_or_create(user=request.user)
        except ShippingAddress.DoesNotExist:
            # Handle case where shipping address is missing
            shipping_user_profile = ShippingAddress.objects.create(user=request.user)

        # Initialize the shipping form with the user's shipping address
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user_profile)

        return render(
            request, 
            'checkout.html', 
            {
                "cart_products": cart_products, 
                'quantities': quantities, 
                'totals': totals, 
                'shipping_form': shipping_form
            }
        )
    else:
        # Checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(
            request, 
            'checkout.html', 
            {
                "cart_products": cart_products, 
                'quantities': quantities, 
                'totals': totals, 
                'shipping_form': shipping_form
            }
        )
 


def billing_info(request):
    if request.method == "POST":
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        # Store shipping information in the session
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Initialize the billing form
        billing_form = PaymentForm()

        return render(
            request, 
            'billing_info.html', 
            {
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "shipping_info": my_shipping,
                "billing_form": billing_form
            }
        )
    else:
        messages.error(request, 'Access denied')
        return redirect('home')




def process_order(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        my_shipping = request.session.get('my_shipping', {})
        full_name = my_shipping.get('shipping_full_name', '')
        email = my_shipping.get('shipping_email', '')
        shipping_address = (
            f"{my_shipping.get('shipping_address1', '')}\n"
            f"{my_shipping.get('shipping_address2', '')}\n"
            f"{my_shipping.get('shipping_city', '')}\n"
            f"{my_shipping.get('shipping_zipcode', '')}\n"
            f"{my_shipping.get('shipping_country', '')}"
        )

        # Create Order
        create_order = Order(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=totals,
        )
        create_order.save()

        # Create Order Items
        for product in cart_products:
            product_id = product.id
            price = product.sale_price if product.is_sale else product.price
            quantity = quantities.get(str(product_id), 0)

            if quantity > 0:
                OrderItem.objects.create(
                    order=create_order,
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    quantity=quantity,
                    price=price,
                )

        # Clear cart and session data
        cart.cart.clear()
        request.session['cart'] = {}
        request.session.pop('my_shipping', None)
        request.session.modified = True

        # Clear cart data in the database for logged-in users
        if request.user.is_authenticated:
            Profile.objects.filter(user=request.user).update(cart_data="")

        messages.success(request, 'Order placed successfully!')
        return redirect('home')
    else:
        messages.error(request, 'Access denied')
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders=Order.objects.filter(shipped=False)

        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']

            order=Order.objects.filter(id=num)
            #grab date and time
            
            now=datetime.datetime.now()
            #update order
            order.update(shipped=True,date_shipped=now)
            #redirect
            messages.success(request,'shipping status updated')  
            return redirect('home')  


        return render(request, "not_shipped_dash.html",{'orders':orders})
    else:    
        messages.success(request, 'Access denied')
        return redirect('home')
def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders=Order.objects.filter(shipped=True)
        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']

            order=Order.objects.filter(id=num)
            #grab date and time
            
            now=datetime.datetime.now()
            #update order
            order.update(shipped=False)
            #redirect
            messages.success(request,'shipping status updated')  
            return redirect('home')  

        return render(request, "shipped_dash.html",{'orders':orders})
    else:    
        messages.success(request, 'Access denied')
        return redirect('home')



def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Fetch the order by its primary key
        order = get_object_or_404(Order, id=pk)
        
        # Get the order items
        items = OrderItem.objects.filter(order=order)

        if request.POST:
            status=request.POST['shipping_status']
            #check if true or false
            if status=='true':
                #get the order
                order=Order.objects.filter(id=pk)
                #update the status
                now=datetime.datetime.now()
                orders.update(shipped=True,date_shipped=now)
            else:
                  #get the order
                order=Order.objects.filter(id=pk)
                #update the status
                order.update(shipped=False)
            messages.success(request,'shipping status updated')  
            return redirect('home')  


        # Render the template
        return render(request, "orders.html", {'order': order, 'items': items})
    else:
        messages.error(request, 'Access denied')
        return redirect('home')    
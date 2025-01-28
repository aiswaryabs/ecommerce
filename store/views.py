from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Category,Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm
from django import forms
from django.db.models import Q
from cart.cart import Cart
from django.contrib.auth.decorators import login_required, user_passes_test
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from .forms import ProductForm,CategoryForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError





# Create your views here.

def home(request):
    products=Product.objects.all()
    return render(request,'home.html',{'products':products})

def about(request):   
    return render(request,'about.html',{})   

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Load the user's cart data if authenticated
            cart = Cart(request)
            cart._load_cart()  # Load the cart data from the profile
            messages.success(request, ('logged in!!'))
            return redirect('home')
        else:
            messages.error(request, ('error'))
            return redirect('login')
    else:
        return render(request, 'login.html', {})




def logout_user(request):
    if request.user.is_authenticated:
        cart = Cart(request)
        cart._save_cart()  # Save the cart data to the user's profile
    logout(request)
    messages.success(request, ('You have been logged out'))
    return redirect('home')
  

def register_user(request):  
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Log in the user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'username created-please fill out your user info below...')
            return redirect('update_info')
        else:
            messages.error(request, 'Whoops! There was a problem registering, please try again...')
            return redirect('register')  # Redirect to the register page for corrections

    # Pass the form to the template
    return render(request, 'register.html', {'form': form})


def product(request,pk):
    product=Product.objects.get(id=pk)
    return render(request,'product.html',{'product':product})


          
def category(request, foo):
    # Normalize the category name by replacing hyphens with spaces
    foo = foo.replace('-', ' ')  
    
    try:
        # Fetch the category using an exact (case-insensitive) match for the name
        category = Category.objects.get(name__iexact=foo)  
        
        # Fetch products belonging to that category
        products = Product.objects.filter(category=category)  
        
        # Return the rendered category template with the category and filtered products
        return render(request, 'category.html', {'products': products, 'category': category})
    
    except Category.DoesNotExist:
        # If the category doesn't exist, show an error message
        messages.error(request, "That Category Doesn't Exist")
        return redirect('home')


def category_summary(request):
    categories=Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})


def update_user(request):
    if request.user.is_authenticated:
        current_user=User.objects.get(id=request.user.id)
        user_form=UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()

            login(request,current_user)
            messages.success(request,'User has been updated!!')
            return redirect('home')

        return render(request,'update_user.html',{'user_form':user_form})   
    else:
        messages.success(request,'You must be logged in to access that page')
        return redirect('home')
def update_password(request):
    if request.user.is_authenticated:
        current_user=request.user
        #did they fill out the form
        if request.method=='POST':
            form=ChangePasswordForm(current_user,request.POST)
            #is the form valid
            if form.is_valid():
                form.save()
                messages.success(request,'Your password has been updated...')
                #ogin(request, user)
                return redirect('update_password')
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error) 
                    return redirect('update_password')   
            
        else:
            form= ChangePasswordForm(current_user) 
              
            return render(request,'update_password.html',{'form':form})  
    else:
        messages.success(request,'You must be logged in to view that page...')
        return redirect('home')


@login_required
def update_info(request):
    try:
        # Try to get the user's profile
        current_user_profile = Profile.objects.get(user=request.user)
        
        # Try to get the user's shipping address
        shipping_user_profile = ShippingAddress.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # If no profile exists, create one
        current_user_profile = Profile.objects.create(user=request.user)
        messages.info(request, 'Your profile was automatically created. Please update it.')
    except ShippingAddress.DoesNotExist:
        # If no shipping address exists, create one
        shipping_user_profile = ShippingAddress.objects.create(user=request.user)
        messages.info(request, 'Your shipping address was automatically created. Please update it.')

    # Now continue with your form logic
    form = UserInfoForm(request.POST or None, instance=current_user_profile)
    shipping_form = ShippingForm(request.POST or None, instance=shipping_user_profile)
    
    if form.is_valid() or shipping_form.is_valid():
        form.save()
        shipping_form.save()
        messages.success(request, 'Your info and shipping address have been updated!')
        return redirect('home')

    return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})


    return render(request, 'update_info.html', {'form': form,'shipping_form':shipping_form})
def search(request):   
    #determine if they filled out the form
    if request.method=='POST':
        searched=request.POST['searched']
        #query the products DB model
        searched=Product.objects.filter(Q(name__icontains=searched) |Q(description__icontains=searched))
        #test for null
        if not searched:
            messages.success(request,'that product does not exist...please try again')

            return render(request,'search.html',{})  

        else:
            return render(request,'search.html',{'searched':searched}) 

    else:
           
        return render(request,'search.html',{})  



# Check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home or product list page
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home or category list page
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})


from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(is_admin)
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Fetch the product to update
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home or product list page
    else:
        form = ProductForm(instance=product)  # Prefill the form with product data

    return render(request, 'update_product.html', {'form': form})



# Delete Products in a single page
@login_required
@user_passes_test(is_admin)
def delete_product(request):
    products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('delete_product')

    return render(request, 'delete_product.html', {'products': products})
@login_required
@user_passes_test(is_admin)
def update_product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'update_product_list.html', {'products': products})


# for admin
def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  # Check if the user is a superuser
                login(request, user)
                return redirect('custom_admin')  # Redirect to the admin panel
            else:
                messages.error(request, 'You do not have permission to access the admin panel.')
                return redirect('login_admin')  # Redirect back to the login page

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login_admin.html')  # Login page template

@login_required
def admin_panel(request):
    # Check if the logged-in user is a superuser
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('login_admin')  # Redirect to login page or any other page

    if request.method == "GET":
        # Fetch data for the admin panel
        users = User.objects.all()
        products = Product.objects.all()
        categories = Category.objects.all()
        return render(request, 'admin_panel.html', {
            'users': users,
            'products': products,
            'categories': categories
        })

    elif request.method == "POST":
        operation = request.POST.get('operation')
        obj_type = request.POST.get('type')

        try:
            # Handling Product Operations
            if operation == "add" and obj_type == "product":
                name = request.POST['name']
                description = request.POST['description']
                price = request.POST['price']
                sale_price = request.POST.get('sale_price')
                rating = request.POST['rating']
                category_id = request.POST['category_id']
                category = get_object_or_404(Category, id=category_id)
                image = request.FILES.get('image')  # Get the uploaded image

                if not image:
                    messages.error(request, "Image is mandatory!")
                    return redirect('custom_admin')

                if sale_price == '':
                    sale_price = 0
                is_sale = bool(sale_price)

                Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    sale_price=sale_price,
                    rating=rating,
                    category=category,
                    image=image,
                    is_sale=is_sale
                )
                messages.success(request, "Product added successfully!")

            elif operation == "update" and obj_type == "product":
                product = get_object_or_404(Product, id=request.POST['id'])
                product.name = request.POST['name']
                product.description = request.POST['description']
                product.price = request.POST['price']
                sale_price = request.POST.get('sale_price')
                product.rating = request.POST['rating']
                product.category = get_object_or_404(Category, id=request.POST['category_id'])

                is_sale = request.POST.get('is_sale') == 'true'

                if not is_sale:
                    product.sale_price = 0
                else:
                    if sale_price == '':
                        sale_price = product.price
                    product.sale_price = sale_price

                product.is_sale = is_sale

                image = request.FILES.get('image')
                if image:
                    product.image = image

                product.save()
                messages.success(request, "Product updated successfully!")

            elif operation == "delete" and obj_type == "product":
                product = get_object_or_404(Product, id=request.POST['id'])
                product.delete()
                messages.success(request, "Product deleted successfully!")

            # Handling User Operations
            elif operation == "add" and obj_type == "user":
                username = request.POST['username']
                email = request.POST['email']
                password = request.POST.get('password')  # Get the password
                is_admin = request.POST.get('is_admin')

                if not password:
                    messages.error(request, "Password is required!")
                    return redirect('custom_admin')

                # Create user with password
                user = User.objects.create_user(username=username, email=email, password=password)
                
                if is_admin:
                    user.is_superuser = True
                    user.is_staff = True
                
                user.save()
                messages.success(request, "User added successfully!")

            elif operation == "update" and obj_type == "user":
                user = get_object_or_404(User, id=request.POST['id'])
                user.username = request.POST['username']
                user.email = request.POST['email']
                user.is_superuser = bool(request.POST.get('is_admin'))
                
                password = request.POST.get('password')  # Get password for update
                if password:
                    user.set_password(password)  # Set the new password if provided
                
                user.save()
                messages.success(request, "User updated successfully!")

            elif operation == "delete" and obj_type == "user":
                user = get_object_or_404(User, id=request.POST['id'])
                user.delete()
                messages.success(request, "User deleted successfully!")

            # Handling Category Operations
            elif operation == "add" and obj_type == "category":
                category_name = request.POST['name']
                Category.objects.create(name=category_name)
                messages.success(request, "Category added successfully!")

            elif operation == "update" and obj_type == "category":
                category = get_object_or_404(Category, id=request.POST['id'])
                category.name = request.POST['name']
                category.save()
                messages.success(request, "Category updated successfully!")

            elif operation == "delete" and obj_type == "category":
                category = get_object_or_404(Category, id=request.POST['id'])
                category.delete()
                messages.success(request, "Category deleted successfully!")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('custom_admin')

from django.shortcuts import render,redirect
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


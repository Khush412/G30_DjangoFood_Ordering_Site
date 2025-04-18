from django.shortcuts import render, redirect #type:ignore
from django.db.models import Q #type:ignore
from django.contrib import messages #type:ignore
from .models import MenuItem, Restaurant #type:ignore
from django.http import JsonResponse #type:ignore
from collections import defaultdict #type:ignore
from django.contrib.auth.forms import UserCreationForm #type:ignore
from django.contrib.auth.models import User #type:ignore
from django.contrib.auth import login, logout #type:ignore
from django.contrib.auth.views import LoginView #type:ignore
from .forms import CustomUserCreationForm #type:ignore
from django.contrib.auth import authenticate #type:ignore
from .forms import LoginForm #type:ignore
from .models import MenuItem, Order, OrderItem #type:ignore
from django.contrib.auth.decorators import login_required #type:ignore
from decimal import Decimal  #type:ignore
from .forms import ContactMessageForm
from django.views.decorators.http import require_POST #type:ignore

# View for the homepage
def restaurant_list(request):
    # Fetch all restaurant objects (no description field as requested)
    restaurants = Restaurant.objects.all()
    
    # Pass restaurants to the context in the template
    return render(request, 'orders/homepage.html', {'restaurants': restaurants})

# View for the Ziggy Cafe menu (your menu page)
def ziggy_cafe_menu(request):
    query = request.GET.get('q', '')
    is_veg = request.GET.get('is_veg', 'all')  # 'veg', 'non-veg', or 'all'
    remove_id = request.GET.get('remove')

    # Base menu items
    menu_items = MenuItem.objects.all()

    # Apply search filter
    if query:
        menu_items = menu_items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Apply veg/non-veg filter
    if is_veg in ['veg', 'non-veg']:
        menu_items = menu_items.filter(is_veg=(is_veg == 'veg'))

    # Categorize menu items for display (filtered result only)
    categorized_menu = defaultdict(list)
    for item in menu_items:
        categorized_menu[item.category.capitalize()].append(item)

    # Get cart from session (initialize if not exists)
    cart = request.session.get('cart', {})

    # Handle Remove from Cart GET request
    if remove_id and remove_id in cart:
        del cart[remove_id]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart!")
        return redirect(f"{request.path}?q={query}&is_veg={is_veg}")

    # Process cart contents
    cart_items = {}
    total_items = 0
    total_price = 0
    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            item_total = item.price * quantity
            cart_items[item_id] = {
                'item': item,
                'quantity': quantity,
                'total_price': item_total
            }
            total_items += quantity
            total_price += item_total
        except MenuItem.DoesNotExist:
            continue  # Skip missing items

    # Handle Add to Cart POST request


    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            cart[item_id] = cart.get(item_id, 0) + 1
            request.session['cart'] = cart
            try:
                item_name = MenuItem.objects.get(id=item_id).name
                message = f"Added {item_name} to cart!"
                if request.POST.get('ajax') == 'true':
                    return JsonResponse({'success': True, 'message': message})
                else:
                    messages.success(request, message)
            except MenuItem.DoesNotExist:
                error_msg = "Item not found."
                if request.POST.get('ajax') == 'true':
                    return JsonResponse({'success': False, 'message': error_msg})
                else:
                    messages.error(request, error_msg)
        return redirect(f"{request.path}?q={query}&is_veg={is_veg}")


    # Final context
    context = {
        'menu_items': menu_items,
        'categorized_menu': dict(categorized_menu),
        'query': query,
        'is_veg': is_veg,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }

    return render(request, 'orders/ziggycafemenu.html', context)

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = {}
    total_price = 0
    total_items = 0

    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            item_total = item.price * quantity
            cart_items[item_id] = {
                'item': item,
                'quantity': quantity,
                'total_price': item_total
            }
            total_price += item_total
            total_items += quantity
        except MenuItem.DoesNotExist:
            continue

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items
    })


def remove_from_cart(request, item_id):
    # Get cart from session
    cart = request.session.get('cart', {})

    # Remove the item from the cart if it exists
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart!")
    else:
        messages.error(request, "Item not found in cart!")

    # Redirect to the cart page
    return redirect('cart')


@require_POST
def update_cart_quantity(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    cart = request.session.get('cart', {})

    if item_id and item_id in cart:
        if action == 'increase':
            cart[item_id] += 1
        elif action == 'decrease':
            cart[item_id] -= 1
            if cart[item_id] <= 0:
                del cart[item_id]  # remove item if quantity goes to 0

    request.session['cart'] = cart
    return redirect('cart')  # redirect back to cart page
# Place order view (unchanged)
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    # Order processing logic here...

    request.session['cart'] = {}  # Clear the cart after order is placed
    messages.success(request, "Order placed successfully!")
    return redirect('checkout')


# Checkout view
def checkout_view(request):
    return render(request, 'orders/checkout.html')

def create_user_view(request):
    # Creating a user programmatically
    user = User.objects.create_user(username="newuser", password="password123", email="newuser@example.com")
    user.save()  # Save the user object to the database
    return redirect('login')  # Redirect to login page after user creation

def signup(request):
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'orders/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            # Authenticate using email and password
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)  # Use username for authentication
                if user is not None:
                    login(request, user)
                    return redirect('homepage')
                else:
                    form.add_error(None, 'Invalid email or password')
            except User.DoesNotExist:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()

    return render(request, 'orders/login.html', {'form': form})

def menu_view(request):
    query = request.GET.get('q', '')
    is_veg = request.GET.get('is_veg', 'all')

    # Filter menu items by search query (if any)
    if query:
        menu_items = MenuItem.objects.filter(name__icontains=query)
    else:
        menu_items = MenuItem.objects.all()

    # Filter by Veg or Non-Veg if selected
    if is_veg == 'veg':
        menu_items = menu_items.filter(is_veg=True)
    elif is_veg == 'non-veg':
        menu_items = menu_items.filter(is_veg=False)

    # Group menu items by category
    categorized_menu = {}
    for item in menu_items:
        if item.category not in categorized_menu:
            categorized_menu[item.category] = []
        categorized_menu[item.category].append(item)

    # Pass categorized_menu to template
    return render(request, 'orders/ziggycafemenu.html', {
        'categorized_menu': categorized_menu,
        'query': query,
        'is_veg': is_veg,
    })

@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    # Get user details from the form (POST data)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        # Calculate the total price from the cart items
        total_price = Decimal(0)
        for item_id, quantity in cart.items():
            try:
                item = MenuItem.objects.get(id=item_id)
                total_price += item.price * quantity
            except MenuItem.DoesNotExist:
                continue  # Skip missing items in cart

        # Create the Order instance in the database
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            address=address,
            phone=phone,
            payment_method=payment_method,
            total_price=total_price
        )

        # Create OrderItems for each item in the cart
        for item_id, quantity in cart.items():
            try:
                item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    product=item,
                    quantity=quantity,
                    price=item.price
                )
            except MenuItem.DoesNotExist:
                continue  # Skip if any item is not found in the menu

        # Clear the cart after the order is placed
        request.session['cart'] = {}

        # Show a success message and redirect
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success')  # You can change this to redirect to a success page

    
def checkout_view(request):
    cart = request.session.get('cart', {})
    cart_items = {}
    total_price = Decimal(0)
    total_items = 0

    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            item_total = item.price * quantity
            cart_items[item_id] = {
                'item': item,
                'quantity': quantity,
                'total_price': item_total
            }
            total_price += item_total
            total_items += quantity
        except MenuItem.DoesNotExist:
            continue

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items
    })

def order_success(request):
    return render(request, 'orders/order_success.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact2')  # Make sure this is a named URL
    else:
        form = ContactMessageForm()
    return render(request, 'orders/contact.html', {'form': form})  # THIS is key


def terms_and_conditions(request):
    return render(request, 'orders/terms_and_conditions.html')
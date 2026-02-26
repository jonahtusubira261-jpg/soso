from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Listing, Category, Conversation, Message, Profile
from .forms import ListingForm, WholesaleForm, ServiceForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TradeGroup, Listing, Cart, CartItem
# --- CART VIEWS ---
from django.http import JsonResponse

from django.db.models import F, Sum


# --- TRADE GROUP VIEWS ---
@login_required
def group_list(request):
    groups = TradeGroup.objects.all()
    return render(request, 'core/groups/list.html', {'groups': groups})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(TradeGroup, id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user) # Auto-join for now
    messages = group.messages.all().order_by('timestamp')
    return render(request, 'core/groups/detail.html', {'group': group, 'messages': messages})


@login_required
def add_to_cart(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, listing=listing)
    
    if not created:
        item.quantity += 1
        item.save()
    
    # Check if request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(i.quantity for i in cart.items.all())
        return JsonResponse({'status': 'ok', 'cart_count': total_items})
    
    # If a normal link click (from cart page), redirect back to cart
    return redirect('core:cart_detail')

@login_required
def reduce_cart_item(request, listing_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, cart=cart, listing_id=listing_id)
    
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
        
    return redirect('core:cart_detail')

@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # Calculate Total Price for the bundle
    # We multiply price by quantity for each item and sum them up
    total_price = 0
    for item in cart.items.all():
        total_price += item.listing.price * item.quantity
        
    return render(request, 'core/cart.html', {
        'cart': cart,
        'total_price': total_price
    })

@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'core/cart.html', {'cart': cart})

# --- DISCOVERY ---
def index(request):
    """The main marketplace feed with filtering"""
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')
    
    # Search logic
    query = request.GET.get('q')
    if query:
        listings = listings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
    # Category filter
    cat_slug = request.GET.get('category')
    if cat_slug:
        listings = listings.filter(category__slug=cat_slug)

    return render(request, 'core/index.html', {'listings': listings})

def product_detail(request, pk):
    """Detail view with dynamic sub-model data"""
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'core/product_detail.html', {'listing': listing})

# --- AUTHENTICATION ---
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login after signup
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

# Logout is handled by Django's built-in LogoutView in URLs

# --- TRADER ACTIONS ---
@login_required
def create_listing(request):
    """The 'Wild West' multi-part form logic"""
    if request.method == 'POST':
        l_form = ListingForm(request.POST, request.FILES)
        # We check forms based on the trade_type selected in the frontend
        if l_form.is_valid():
            listing = l_form.save(commit=False)
            listing.trader = request.user
            listing.save()
            
            # Save Wholesale details if applicable
            if listing.trade_type == 'WHOLESALE':
                w_form = WholesaleForm(request.POST)
                if w_form.is_valid():
                    w_obj = w_form.save(commit=False)
                    w_obj.listing = listing
                    w_obj.save()
            
            # Save Service details if applicable
            elif listing.trade_type == 'SERVICE':
                s_form = ServiceForm(request.POST)
                if s_form.is_valid():
                    s_obj = s_form.save(commit=False)
                    s_obj.listing = listing
                    s_obj.save()
            
            return redirect('product_detail', pk=listing.pk)
    else:
        l_form = ListingForm()
        w_form = WholesaleForm()
        s_form = ServiceForm()
        
    return render(request, 'core/create_listing.html', {
        'l_form': l_form, 
        'w_form': w_form, 
        's_form': s_form
    })


# --- SOCIAL/NEGOTIATION ---
@login_required
def negotiate(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    
    # Don't let traders talk to themselves
    if listing.trader == request.user:
        return redirect('core:product_detail', pk=pk)

    # Find or create a unique conversation for this specific buyer, trader, and item
    convo, created = Conversation.objects.get_or_create(
        buyer=request.user,
        trader=listing.trader,
        listing=listing
    )
    
    # Redirect to the chat page (ensure this URL name exists in your urls.py)
    return render(request, 'core/chat.html', {'conversation': convo})
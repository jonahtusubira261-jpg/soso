from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Listing, Category, Conversation, Message, Profile
from .forms import ListingForm, WholesaleForm, ServiceForm

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
    """Start or resume a 1-on-1 haggling session"""
    listing = get_object_or_404(Listing, pk=pk)
    
    if listing.trader == request.user:
        return redirect('product_detail', pk=pk) # Can't haggle with yourself

    convo, created = Conversation.objects.get_or_create(
        buyer=request.user,
        trader=listing.trader,
        listing=listing
    )
    return render(request, 'core/chat.html', {'conversation': convo})
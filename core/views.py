from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.urls import reverse
from .models import Listing, Category, Conversation, Message, Profile, Cart, CartItem, TradeGroup
from .forms import ListingForm, WholesaleForm, ServiceForm, SosoSignupForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
import json

def index(request):
    listings = Listing.objects.filter(is_active=True).select_related('category', 'trader__profile').order_by('-created_at')
    featured_listings = listings[:5]  # First 5 for carousel
    categories = Category.objects.filter(parent=None)
    
    return render(request, 'core/index.html', {
        'listings': listings,
        'featured_listings': featured_listings,
        'categories': categories
    })

def product_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    related_listings = Listing.objects.filter(
        category=listing.category, 
        is_active=True
    ).exclude(pk=pk)[:4]
    
    return render(request, 'core/product_detail.html', {
        'listing': listing,
        'related_listings': related_listings
    })

@login_required
def add_to_cart(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, listing=listing)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_count': total_items,
            'message': f'{listing.title} added to bundle'
        })
    
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
    cart_items = cart.items.all().select_related('listing')
    total_price = sum(item.listing.price * item.quantity for item in cart_items)
    item_count = cart_items.count()
    
    return render(request, 'core/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'item_count': item_count
    })

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.trader:
        return redirect('core:index')
    
    listing.delete()
    return redirect('core:index')

def search_autocomplete(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    listings = Listing.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).select_related('category')[:10]
    
    results = []
    for listing in listings:
        results.append({
            'id': listing.id,
            'title': listing.title,
            'price': str(listing.price),
            'image_url': listing.media_url if listing.media else '/static/images/default-placeholder.png',
            'category': listing.category.name,
            'url': reverse('core:product_detail', args=[listing.id])
        })
    
    return JsonResponse({'results': results})

def signup(request):
    if request.method == 'POST':
        form = SosoSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:index')
    else:
        form = SosoSignupForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def create_listing(request):
    if request.method == 'POST':
        l_form = ListingForm(request.POST, request.FILES)
        if l_form.is_valid():
            listing = l_form.save(commit=False)
            listing.trader = request.user
            listing.save()
            
            if listing.trade_type == 'WHOLESALE':
                w_form = WholesaleForm(request.POST, instance=listing)
                if w_form.is_valid():
                    w_form.save()
            elif listing.trade_type == 'SERVICE':
                s_form = ServiceForm(request.POST, instance=listing)
                if s_form.is_valid():
                    s_form.save()
            
            return redirect('core:product_detail', pk=listing.pk)
    else:
        l_form = ListingForm()
        w_form = WholesaleForm()
        s_form = ServiceForm()
    
    return render(request, 'core/create_listing.html', {
        'l_form': l_form,
        'w_form': w_form,
        's_form': s_form
    })

@login_required
def negotiate(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user == listing.trader:
        return redirect('core:product_detail', pk=pk)
    
    conversation, created = Conversation.objects.get_or_create(
        buyer=request.user,
        trader=listing.trader,
        listing=listing
    )
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    
    return render(request, 'core/chat.html', {
        'conversation': conversation,
        'listing': listing,
        'messages': messages
    })

@login_required
def group_list(request):
    groups = TradeGroup.objects.all()
    return render(request, 'core/groups/list.html', {'groups': groups})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(TradeGroup, id=group_id)
    if request.user not in group.members.all():
        group.members.add(request.user)
    messages = group.messages.all().order_by('timestamp')
    return render(request, 'core/groups/detail.html', {'group': group, 'messages': messages})
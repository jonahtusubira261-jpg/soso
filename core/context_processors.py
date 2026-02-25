from .models import Category, Cart

def soso_global_data(request):
    # Get top-level categories for the Mega Menu
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    
    # Handle Cart logic for Auth and Guest users
    cart_count = 0
    session_key = request.session.session_key
    
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    elif session_key:
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    else:
        cart = None
        
    if cart:
        cart_count = cart.items.count()

    return {
        'nav_categories': categories,
        'cart_count': cart_count
    }
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('negotiate/<int:pk>/', views.negotiate, name='negotiate'),
    
    # Auth Routes
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/reduce/<int:listing_id>/', views.reduce_cart_item, name='reduce_cart_item'),
    path('add-to-cart/<int:listing_id>/', views.add_to_cart, name='add_to_cart'),
        
    # Trader Actions
    path('list-item/', views.create_listing, name='create_listing'),
] # <--- Ensure this is a bracket, not a comma
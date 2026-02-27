from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from core.views import health_check

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('negotiate/<int:pk>/', views.negotiate, name='negotiate'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:index'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/reduce/<int:listing_id>/', views.reduce_cart_item, name='reduce_cart_item'),
    path('add-to-cart/<int:listing_id>/', views.add_to_cart, name='add_to_cart'),
    path('list-item/', views.create_listing, name='create_listing'),
    path('delete-listing/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('search/', views.search_autocomplete, name='search'),
    path('health/', health_check, name='health_check',
]

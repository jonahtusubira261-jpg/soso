from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import health_check


urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Core App URLs
    path('', include('core.urls')),
    
    # Built-in Auth Handlers
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('health/', health_check, name='health_check'),
]

# Essential for showing product images during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

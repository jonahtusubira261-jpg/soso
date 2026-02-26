from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class TradeGroup(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    members = models.ManyToManyField(User, related_name="trade_groups")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(TradeGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_trader = models.BooleanField(default=False)
    avatar = CloudinaryField('avatar', folder='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    trust_score = models.IntegerField(default=100)
    location_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.user.username

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    trader = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews_received')
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_service = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Listing(models.Model):
    TRADE_TYPES = (
        ('RETAIL', 'Retail'),
        ('WHOLESALE', 'Wholesale'),
        ('SERVICE', 'Service/Hailing'),
        ('AUCTION', 'Live Auction'),
    )
    CONDITION = (
        ('NEW', 'Brand New'),
        ('USED', 'Second Hand'),
        ('NONE', 'N/A (Services)'),
    )
    
    trader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    media = CloudinaryField('media', folder='listings/', resource_type='auto', blank=True, null=True)
    
    @property
    def media_url(self):
        if self.media:
            return self.media.url
        return '/static/images/default-placeholder.png'
    
    @property
    def is_video(self):
        if self.media:
            return self.media.resource_type == 'video'
        return False
    
    price = models.DecimalField(max_digits=12, decimal_places=2)
    trade_type = models.CharField(max_length=20, choices=TRADE_TYPES, default='RETAIL')
    condition = models.CharField(max_length=10, choices=CONDITION, default='NEW')
    auction_end = models.DateTimeField(null=True, blank=True)
    current_highest_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def time_remaining(self):
        if self.trade_type == 'AUCTION' and self.auction_end:
            remaining = self.auction_end - timezone.now()
            return remaining if remaining.total_seconds() > 0 else None
        return None
    
    def __str__(self):
        return self.title

class WholesaleDetail(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='wholesale_data')
    min_order_qty = models.PositiveIntegerField(default=1)
    unit_name = models.CharField(max_length=50, default='unit')

class ServiceDetail(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='service_data')
    is_available = models.BooleanField(default=True)
    vehicle_info = models.CharField(max_length=100, blank=True, null=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_buyer')
    trader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_trader')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('buyer', 'trader', 'listing')

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    is_offer = models.BooleanField(default=False)
    offered_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    offer_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.listing.title}"
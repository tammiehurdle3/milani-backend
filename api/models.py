from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# --- Custom User Manager ---
class CreatorManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email: raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

# --- Custom User ---
class Creator(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CreatorManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self): return self.email

# --- Creator Profile ---
class CreatorProfile(models.Model):
    creator = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    # Public Persona
    bio = models.TextField(blank=True, null=True)
    profile_picture_url = models.URLField(max_length=1024, blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True) # {'instagram': '@...', 'tiktok': '@...'}
    tier = models.CharField(max_length=50, default="Muse Tier") # Editable by admin

    # Verification & Onboarding
    verification_status = models.CharField(
        max_length=20, default='unverified',
        choices=[('unverified', 'Unverified'), ('pending', 'Pending'), ('verified', 'Verified')]
    )
    w9_complete = models.BooleanField(default=False)
    w9_data_encrypted = models.TextField(blank=True, null=True)
    
    # ID Images
    id_front_image = models.TextField(blank=True, null=True)
    id_back_image = models.TextField(blank=True, null=True)
    selfie_image = models.TextField(blank=True, null=True)

    # Campaign Specifics (Per Creator)
    contract_signed = models.BooleanField(default=False)
    product_shipped = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    personalized_compensation = models.CharField(max_length=100, blank=True, null=True, help_text="Overrides default campaign rate (e.g. '$1,500')")
    personalized_deadline = models.DateField(blank=True, null=True, help_text="Overrides default campaign deadline")


    def __str__(self): return f"{self.creator.username}'s Profile"

# --- Signals ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_creator_profile(sender, instance, created, **kwargs):
    if created:
        CreatorProfile.objects.create(creator=instance)
    else:
        instance.profile.save()

# --- Campaign Model ---
class Campaign(models.Model):
    title = models.CharField(max_length=200) # "Face Set. Mind Set."
    phase = models.CharField(max_length=100, default="Phase 1")
    description = models.TextField()
    
    # Assets
    cover_image = models.URLField(blank=True, null=True)
    brief_pdf_url = models.URLField(blank=True, null=True)
    
    # Logic
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    
    # Compensation Display
    compensation_rate = models.CharField(max_length=100, default="$100.00")
    usage_rights = models.CharField(max_length=100, default="+ Usage Rights")

    def __str__(self): return self.title

# --- Content Submission ---
class ContentSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Changes Requested'),
    ]
    
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, related_name='submissions')
    
    # We store the URL (from S3 or Cloudinary)
    content_url = models.URLField(max_length=2048) 
    file_type = models.CharField(max_length=10, default='video') # 'video' or 'image'
    
    # Platform Field (Fixed)
    platform = models.CharField(
        max_length=50, 
        choices=[('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('youtube', 'YouTube')], 
        default='tiktok'
    ) 
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.creator.username} - {self.status}"

class InviteCode(models.Model):
    code = models.CharField(max_length=50, unique=True) # e.g. "MILANI-SARAH"
    email = models.EmailField(unique=True) # Lock this code to one email
    first_name = models.CharField(max_length=100)
    tier = models.CharField(max_length=50, default="Muse Tier")
    
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.email} ({'Used' if self.is_used else 'Available'})"
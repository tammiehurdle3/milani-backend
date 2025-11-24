from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Creator, CreatorProfile, Campaign, ContentSubmission, InviteCode

class CreatorAdmin(UserAdmin):
    model = Creator
    list_display = ('email', 'username', 'is_staff', 'date_joined')
    list_filter = ('is_active',)
    search_fields = ('email', 'username')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ('creator', 'verification_status', 'tier', 'contract_signed', 'product_shipped')
    list_editable = ('verification_status', 'tier', 'contract_signed', 'product_shipped')
    search_fields = ('creator__email', 'creator__username')
    fieldsets = (
        ('Creator Info', {'fields': ('creator', 'bio', 'social_links', 'profile_picture_url')}),
        ('Status', {'fields': ('tier', 'verification_status')}),
        ('Onboarding & Tracking', {'fields': ('contract_signed', 'product_shipped', 'tracking_number', 'tracking_url')}),
        ('Legal', {'fields': ('w9_complete', 'w9_data_encrypted', 'id_front_image', 'selfie_image')}),
    )

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'phase', 'is_active', 'deadline')
    list_editable = ('is_active', 'phase', 'deadline')

class SubmissionAdmin(admin.ModelAdmin):
    # Added 'platform' back since the model is confirmed to have it
    list_display = ('creator', 'campaign', 'platform', 'status', 'created_at')
    list_filter = ('status', 'platform')
    list_editable = ('status',)

class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'email', 'first_name', 'is_used', 'created_at')
    list_filter = ('is_used', 'tier')
    search_fields = ('code', 'email')

admin.site.register(Creator, CreatorAdmin)
admin.site.register(CreatorProfile, CreatorProfileAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(ContentSubmission, SubmissionAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)
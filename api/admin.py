from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import Creator, CreatorProfile, Campaign, ContentSubmission, InviteCode

class CreatorAdmin(UserAdmin):
    model = Creator
    list_display = ('email', 'username', 'is_staff', 'date_joined')
    list_filter = ('is_active',)
    search_fields = ('email', 'username')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

class CreatorProfileAdmin(admin.ModelAdmin):
    # Added new helper fields to list_display
    list_display = ('creator', 'verification_status', 'tier', 'contract_signed', 'product_shipped', 'id_front_image_tag')
    list_editable = ('verification_status', 'tier', 'contract_signed', 'product_shipped')
    search_fields = ('creator__email', 'creator__username')
    
    # FIX: Add the custom methods to readonly_fields so Django knows they are fields on the Admin class, not the model.
    readonly_fields = ('w9_data_encrypted', 'id_front_image_tag', 'id_back_image_tag', 'selfie_image_tag') 

    # Updated fieldsets to include both the raw data and the helper preview
    fieldsets = (
        ('Creator Info', {'fields': ('creator', 'bio', 'social_links', 'profile_picture_url')}),
        ('Status', {'fields': ('tier', 'verification_status')}),
        ('Onboarding & Tracking', {'fields': ('contract_signed', 'product_shipped', 'tracking_number', 'tracking_url')}),
        # NEW SECTION: Viewable Base64 Data
        ('Legal & Verification', {'fields': ('w9_complete', 'w9_data_encrypted', 
                                            'id_front_image', 'id_front_image_tag', 
                                            'id_back_image', 'id_back_image_tag', 
                                            'selfie_image', 'selfie_image_tag')}),
    )

    # Helper method to display ID Front image in Admin
    def id_front_image_tag(self, obj):
        if obj.id_front_image:
            # We wrap the Base64 string in an HTML img tag
            return mark_safe(f'<img src="{obj.id_front_image}" width="150" height="auto" />')
        return "No Image"
    id_front_image_tag.short_description = 'ID Front Preview'
    id_front_image_tag.allow_tags = True
    
    # Helper method to display ID Back image in Admin
    def id_back_image_tag(self, obj):
        if obj.id_back_image:
            return mark_safe(f'<img src="{obj.id_back_image}" width="150" height="auto" />')
        return "No Image"
    id_back_image_tag.short_description = 'ID Back Preview'
    id_back_image_tag.allow_tags = True
    
    # Helper method to display Selfie image in Admin
    def selfie_image_tag(self, obj):
        if obj.selfie_image:
            return mark_safe(f'<img src="{obj.selfie_image}" width="150" height="auto" />')
        return "No Image"
    selfie_image_tag.short_description = 'Selfie Preview'
    selfie_image_tag.allow_tags = True


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
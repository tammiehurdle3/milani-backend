from rest_framework import serializers
from .models import Creator, CreatorProfile, Campaign, ContentSubmission
from django.contrib.auth.password_validation import validate_password

# --- Auth ---
class CreatorSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = Creator
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return Creator.objects.create_user(**validated_data)

# --- Profile ---
class CreatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorProfile
        fields = [
            'bio', 'social_links', 'profile_picture_url', 'tier',
            'verification_status', 'w9_complete',
            'contract_signed', 'product_shipped', 'tracking_number', 'tracking_url'
        ]
        # These fields should be read-only for the creator (admin edits them)
        read_only_fields = [
            'tier', 'verification_status', 'w9_complete', 
            'contract_signed', 'product_shipped', 'tracking_number', 'tracking_url'
        ]

# --- Main User ---
class CreatorSerializer(serializers.ModelSerializer):
    profile = CreatorProfileSerializer(read_only=True)
    
    # We'll include the active campaign status here for easy frontend access
    active_campaign = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()

    class Meta:
        model = Creator
        fields = ['id', 'username', 'email', 'profile', 'active_campaign', 'submission_status']

    def get_active_campaign(self, obj):
        # Logic: Get the most recent active campaign
        campaign = Campaign.objects.filter(is_active=True).first()
        if campaign:
            return CampaignSerializer(campaign).data
        return None
    def get_submission_status(self, obj):
        campaign = Campaign.objects.filter(is_active=True).first()
        if not campaign:
            return "no_campaign"

        submission = ContentSubmission.objects.filter(creator=obj, campaign=campaign).first()
        
        if submission:
            return submission.status # Returns 'pending', 'approved', or 'rejected'
        return "pending_upload" # Default if no submission found

# --- Campaign ---
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

# --- Submissions ---
class ContentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentSubmission
        fields = '__all__'
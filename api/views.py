from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Campaign, ContentSubmission, InviteCode
from .serializers import (
    CreatorSignUpSerializer,
    CreatorSerializer,
    CreatorProfileSerializer,
    CampaignSerializer,
    ContentSubmissionSerializer
)
import json

# --- Optional: Test Route ---------------------------------------------------

@api_view(['GET'])
def get_routes(request):
    """
    Quick test to confirm API is operational.
    """
    routes = [
        '/api/auth/login/',
        '/api/auth/signup/',
        '/api/auth/me/',
        '/api/profile/',
        '/api/campaigns/',
        '/api/submissions/'
    ]
    return Response(routes)


# --- Auth -------------------------------------------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    JWT login. Accepts email + password.
    """
    pass

class VerifyInviteView(APIView):
    """
    Checks if an Invite Code is valid and unused.
    Returns the user's pre-filled details.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        
        try:
            invite = InviteCode.objects.get(code=code)
            
            if invite.is_used:
                return Response(
                    {"detail": "This code has already been claimed."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Return the info to the frontend so we can say "Welcome, Sarah!"
            return Response({
                "valid": True,
                "email": invite.email,
                "first_name": invite.first_name,
                "tier": invite.tier
            })
            
        except InviteCode.DoesNotExist:
            return Response(
                {"detail": "Invalid access code."}, 
                status=status.HTTP_404_NOT_FOUND
            )


class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # 1. We expect the code to be passed along with the signup data
        code = request.data.get('code')
        
        # 2. Optional: Validate code again just to be safe
        try:
            invite = InviteCode.objects.get(code=code)
        except InviteCode.DoesNotExist:
             # For dev testing you might skip this, but in prod you want this check
             pass 

        # 3. Create the user (Existing Logic)
        serializer = CreatorSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # 4. MARK CODE AS USED!
            if code and invite:
                invite.is_used = True
                invite.save()

            return Response(
                {"message": "User created successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentCreatorView(APIView):
    """
    Protected. Returns:
    - User info
    - User profile info
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = CreatorSerializer(request.user)
        return Response(serializer.data)


# --- Profile + Verification --------------------------------------------------

class CreatorProfileView(APIView):
    """
    Allows creator to view + update their profile.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = CreatorProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def patch(self, request):
        """
        Safely update bio/social links/picture.
        Only allows specific fields to prevent unauthorized modifications.
        """
        profile = request.user.profile

        allowed_fields = {
            'bio': request.data.get('bio'),
            'social_links': request.data.get('social_links'),
            'profile_picture_url': request.data.get('profile_picture_url')
        }

        clean_data = {k: v for k, v in allowed_fields.items() if v is not None}

        serializer = CreatorProfileSerializer(
            profile, data=clean_data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitVerificationView(APIView):
    """
    Handles ID front/back, selfie, and W9 submission.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        profile = request.user.profile

        # Save image fields
        profile.id_front_image = request.data.get('id_front')
        profile.id_back_image = request.data.get('id_back')
        profile.selfie_image = request.data.get('selfie')

        # W9 data (stored encrypted — replace with real encryption later)
        w9_data = request.data.get('w9')
        if w9_data:
            profile.w9_complete = True
            profile.w9_data_encrypted = json.dumps(w9_data)

        # Status update
        profile.verification_status = 'pending'
        profile.save()

        return Response(
            {"status": "pending", "message": "Verification submitted."},
            status=status.HTTP_200_OK
        )


# --- Campaigns --------------------------------------------------------------

class CampaignListView(APIView):
    """
    Returns list of active campaigns.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        campaigns = Campaign.objects.filter(
            is_active=True
        ).order_by('-created_at')

        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)


# --- Submissions ------------------------------------------------------------

class SubmissionListView(APIView):
    """
    List + create content submissions for logged-in creator.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        submissions = ContentSubmission.objects.filter(
            creator=request.user
        ).order_by('-created_at')

        serializer = ContentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        serializer = ContentSubmissionSerializer(data=data)

        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


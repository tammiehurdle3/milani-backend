from django.urls import path
from . import views

urlpatterns = [
    # --- Test ---
    path('', views.get_routes, name='routes'),
    
    # --- Auth ---
    path('auth/verify-invite/', views.VerifyInviteView.as_view(), name='verify_invite'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/me/', views.CurrentCreatorView.as_view(), name='current_user'),

    # --- Dashboard ---
    path('profile/', views.CreatorProfileView.as_view(), name='profile'),

    #Campaign
    path('campaigns/', views.CampaignListView.as_view(), name='campaigns'),

    path('submissions/', views.SubmissionListView.as_view(), name='submissions'),

]
"""
URL configuration for creator_portal_backend project.
"""
from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line tells Django to look at 'api/urls.py' 
    # for any URL starting with 'api/'
    path('api/', include('api.urls')), 
]
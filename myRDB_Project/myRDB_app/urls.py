from django.conf.urls import url
from django.urls import path, include

from . import views

app_name = 'myRDB'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('password_reset/', views.Password_Reset.as_view(), name='password_reset'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('profile/rights_analysis', views.ProfileRightsAnalysis.as_view(), name='profile_rights_analysis'),
    path('profile/compare/', views.Compare.as_view(), name='compare'),
    path('csvToMongo/', views.CSVtoMongoDB.as_view(), name='csvToMongo'),
    path('users/', views.Users.as_view(), name='users'),
    path('search_all/', views.Search_All.as_view(), name='search_all'),
    path('apply_changes/', views.DigitalRightApplication.as_view(), name='apply_changes'),
]

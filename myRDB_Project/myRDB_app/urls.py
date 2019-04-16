from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth.decorators import login_required,permission_required

from . import views

app_name = 'myRDB'
urlpatterns = [
    #path('', include('django.contrib.auth.urls')),
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('password_reset/', views.Password_Reset.as_view(), name='password_reset'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/', login_required(views.Profile.as_view()), name='profile'),
    path('profile/rights_analysis', login_required(views.ProfileRightsAnalysis.as_view()), name='profile_rights_analysis'),
    path('profile/compare/', login_required(views.Compare.as_view()), name='compare'),
    path('csvToMongo/', permission_required('user.is_staff')(views.CSVtoMongoDB.as_view()), name='csvToMongo'),
    path('users/', permission_required('user.is_staff')(views.Users.as_view()), name='users'),
    path('search_all/', permission_required('user.is_staff')(views.Search_All.as_view()), name='search_all'),
    path('request_pool/', permission_required('user.is_staff')(views.RequestPool.as_view()), name='request_pool'),
    path('my_requests/', login_required(views.MyRequests.as_view()), name='my_requests'),
    path('profile/compare/apply_changes/', login_required(views.RightApplication.as_view()), name='apply_changes'),
]

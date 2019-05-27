"""myRDB_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from myRDB_app import views

from . import settings

'''
    sets REST-API urls
'''
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'user')
router.register(r'roles', views.RoleViewSet, 'role')
router.register(r'afs', views.AFViewSet, 'af')
router.register(r'gfs', views.GFViewSet, 'gf')
router.register(r'tfs', views.TFViewSet, 'tf')
router.register(r'orgas', views.OrgaViewSet, 'orga')
router.register(r'groups', views.GroupViewSet, 'group')
router.register(r'departments', views.DepartmentViewSet, ' department')
router.register(r'zi_organisations', views.ZI_OrganisationViewSet, 'zi_organisation')
router.register(r'tf_applications', views.TF_ApplicationViewSet, 'tf_application')
router.register(r'usermodelrights', views.UserModelRightsViewSet, 'usermodelrights')
router.register(r'userlistings', views.UserListingViewSet, 'userlisting')
router.register(r'searchlistings', views.CompleteUserListingViewSet, 'searchlisting')
router.register(r'changerequests', views.ChangeRequestsViewSet, 'changerequests')

urlpatterns = [
    url(r'^', include(router.urls)),
    path('', include('django.contrib.auth.urls')),
    path('myRDB/', include('myRDB_app.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

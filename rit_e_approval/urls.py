"""
URL configuration for rit_e_approval project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from application import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_form', views.create_form, name="create_form"),
    path('signup', views.signup, name="signup"),
    path('', views.login, name="login"),
    path('view_approval', views.view_approval, name="view_approval"),
    path('auth_approval', views.auth_approval, name="auth_approval"),
    path('clarification', views.clarification, name="clarification"),
    path('approval_user_details',views.approval_user_details,name="approval_user_details"),
    path('updateapproval',views.updateapproval,name="updateapproval"),
    path('form_approval',views.form_approval,name="form_approval")

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
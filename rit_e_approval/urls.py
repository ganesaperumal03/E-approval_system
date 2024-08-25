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
from django.contrib import admin #type:ignore
from django.urls import path #type:ignore
from application import views #type:ignore
from django.conf import settings #type:ignore
from django.conf.urls.static import static #type:ignore
urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_form', views.create_form, name="create_form"),
    path('signup', views.signup, name="signup"),
    path('', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('view_approval', views.view_approval, name="view_approval"),
    path('select', views.select, name="select"),
    path('auth_approval', views.auth_approval, name="auth_approval"),
    path('clarification', views.clarification, name="clarification"),
    path('update_allotment', views.update_allotment, name="update_allotment"),
    path('allottment', views.allottment, name="allottment"),
    path('allotting',views.allotting,name="allotting"),
    path('updateapproval',views.updateapproval,name="updateapproval"),
    path('form_approval',views.form_approval,name="form_approval"),
    path('reject_approval',views.reject_approval,name="reject_approval"),
    path('form_edit',views.form_edit,name="form_edit"),
    path('table', views.table, name='table'),
    path('pdf_show',views.pdf_show,name="pdf_show"),
    path('create_pdf_show',views.create_pdf_show,name="create_pdf_show"),
    path('form_delete',views.form_delete,name="form_delete"),
    path('send_email',views.send_email,name="send_email"),
    path('create_save',views.create_save,name="create_save"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('process_department/', views.process_department, name='process_department'),
    path('pdf/', views.pdf, name='pdf'),
    path('pdf_show/<path:Tran_No>/', views.pdf_show, name='pdf_show'),
    path('generate_pdf/<path:Tran_No>/', views.generate_pdf, name='generate_pdf'),

    # path('get_subcategories/<str:category>/', views.get_subcategories, name='get_subcategories'),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
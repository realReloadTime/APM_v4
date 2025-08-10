from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # path('', TemplateView.as_view(template_name='core/information_page.html'), name='home'),
    path('register/', TemplateView.as_view(template_name='core/register.html'), name='register'),
    path('login/', TemplateView.as_view(template_name='core/login.html'), name='login'),
    path('form/', TemplateView.as_view(template_name='core/form_page.html'), name='form'),
    path('table/', TemplateView.as_view(template_name='core/table_page.html'), name='table'),
    path('navbar/', TemplateView.as_view(template_name='core/navbar.html'), name='navbar'),
    path('information/', TemplateView.as_view(template_name='core/information_page.html'), name='information')
]
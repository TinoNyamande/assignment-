from django.urls import path
from . import views

urlpatterns = [
    path('', views.validate, name='validate_root'),
    path('validate/', views.validate, name='validate'),
    path('analyze/', views.analyze_file, name='analyze'),
]

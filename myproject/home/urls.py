from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path('', views.index, name='index'),
    path('data/', views.data_page, name='data_page'),
    
    # API v1 (versioned endpoints)
    path('api/v1/data/', views.data_api, name='data_api_v1'),
    path('api/v1/enrollment-graph/', views.enrollment_graph, name='enrollment_graph_v1'),
    
    # Legacy API routes (backward compatibility - will redirect to v1)
    path('api/data/', views.data_api, name='data_api'),
    path('api/enrollment-graph/', views.enrollment_graph, name='enrollment_graph'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RunningEventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.RunningEventDetailView.as_view(), name='event_detail'),
    path('registration-success/<int:pk>/', views.RegistrationSuccessView.as_view(), name='registration_success'),
    path('already-registered/<int:pk>/', views.AlreadyRegisteredView.as_view(), name='already_registered'),
]

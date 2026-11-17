from django.urls import path

from . import views

urlpatterns = [
    path('', views.GroupListCreate.as_view()),
    path('<uuid:pk>/', views.GroupDetail.as_view()),
]

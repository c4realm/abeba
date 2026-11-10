from django.urls import path

from . import views

urlpatterns = [
    path('health/', views.health),
    path('internal/run-deadlines/', views.RunDeadlines.as_view()),
]

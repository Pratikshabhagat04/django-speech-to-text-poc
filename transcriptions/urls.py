from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("record/", views.create_page, name="create"),
    path("record/<int:pk>/", views.detail, name="detail"),
    path("record/<int:pk>/edit/", views.update, name="update"),
    path("record/<int:pk>/delete/", views.delete, name="delete"),
]

from . import views
from django.urls import path
from .views import GeneratePdf

urlpatterns = [
    path('', views.home ),
    path('ts/', views.importLatestTimesheets ),
    path('statement', views.DisplayStatement ),
    path('stat',views.Statement.as_view(),name="stat"),
    path('pdf/', views.GeneratePdf.as_view()),
]
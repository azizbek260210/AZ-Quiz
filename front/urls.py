from . import views
from django.urls import path

app_name = 'front'

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz-detail/<str:code>/', views.quiz_detail, name='quiz_detail'),
]
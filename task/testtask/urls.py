from django.urls import path
from .import views


urlpatterns = [
    path('index.html', views.IndexHTMLView.as_view(), name='task_html'),
    path('index.json', views.IndexJsonView.as_view(), name='task_json')
]

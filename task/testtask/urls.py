from django.urls import path
from .import views


urlpatterns = [
    path('html', views.IndexHTMLView.as_view(), name='task_html'),
    path('json', views.IndexJsonView.as_view(), name='task_json')
]

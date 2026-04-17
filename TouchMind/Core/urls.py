from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'), # 画面を表示
    path('api/record/', views.record_event, name = 'record_event'), ## API検証用
    path('list/', views.event_list, name = 'event_list'), ## 保存されたイベントの一覧表示
]
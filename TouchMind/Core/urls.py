from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'), # 画面を表示

    path('api/record/', views.record_event, name = 'record_event'), ## API検証用
    path('api/graph-data/', views.graph_api, name = 'graph_api'),
    path('api/personal-graph-data/', views.personal_graph_api, name = 'personal_graph_api'),

    path('list/', views.event_list, name = 'event_list'), ## 保存されたイベントの一覧表示
    path('personal-list/', views.personal_event_list, name='personal_event_list'),

    path('signup/', views.signup, name = 'signup'), ## 新規ユーザー登録画面

    path('graph/', views.graph_view, name = 'graph_view'),
    path('personal-graph/', views.personal_graph_view, name = 'personal_graph_view'),
]
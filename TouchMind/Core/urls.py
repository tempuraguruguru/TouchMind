from django.urls import path
from . import views

urlpatterns = [
    # 画面表示用のURL
    path('', views.index, name = 'index'), # 画面を表示

    # APIエンドポイント
    path('api/record/', views.record_event, name = 'record_event'), ## API検証用
    path('api/graph-data/', views.graph_api, name = 'graph_api'),
    path('api/personal-graph-data/', views.personal_graph_api, name = 'personal_graph_api'),

    # 画面表示用のURL
    path('list/', views.event_list, name = 'event_list'), ## 保存されたイベントの一覧表示
    path('personal-list/', views.personal_event_list, name='personal_event_list'),

    # ユーザー認証関連のURL
    path('signup/', views.signup, name = 'signup'), ## 新規ユーザー登録画面

    # 追加の画面ルーティング
    path('graph/', views.graph_view, name = 'graph_view'),
    path('personal-graph/', views.personal_graph_view, name = 'personal_graph_view'),

    # APIエンドポイント：個人化された提案を返す
    path('api/personalized-suggestion/', views.personalized_suggestion_api, name = 'personalized_suggestion_api'),

    # 場所管理の画面とAPI
    path('locations/', views.location_manager_view, name = 'location_manager'),
    path('api/get-locations/', views.get_locations_api, name = 'get_locations_api'),
    path('api/bulk-add-locations/', views.bulk_add_locations_api, name = 'bulk_add_locations_api'),
    path('api/update-location/', views.update_location_api, name = 'update_location_api'),
    path('api/delete-location/', views.delete_location_api, name = 'delete_location_api'),
]
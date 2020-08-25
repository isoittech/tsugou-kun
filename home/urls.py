from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('event/', views.event_list, name='event_list'),  # 一覧
    path('event/add/', views.event_add, name='event_add'),  # 登録
    path('event/kouho/', views.event_kouho_print, name='event_kouho'),  # イベント日時候補
    path('event/notify_event_add_completed/', views.notify_event_add_completed, name='notify_event_add_completed'),  # イベント追加完了
    path('event/fill/', views.schedule_fill, name='schedule_fill'),  # 参加可否記入
    path('event/mod/<int:event_id>/', views.event_edit, name='event_mod'),  # 修正
    path('event/del/<int:event_id>/', views.event_del, name='event_del'),  # 削除
    path('', views.index, name='index'),
]

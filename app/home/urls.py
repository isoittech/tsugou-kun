from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('event/add/', views.event_add, name='event_add'),  # 登録
    path('event/edit/', views.event_edit_prepare, name='event_edit_prepare'),  # 編集
    path('event/kouho/', views.event_kouho_print, name='event_kouho'),  # イベント日時候補
    path('event/notify_event_add_completed/', views.notify_event_add_completed, name='notify_event_add_completed'),  # イベント追加完了
    path('event/fill/', views.schedule_fill, name='schedule_fill'),  # 参加可否記入
    path('', views.index, name='index'),
]

from django.contrib import admin

from home.models import Event, Sankasha, SankaNichiji, EventKouhoNichiji


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'memo',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目


admin.site.register(Event, EventAdmin)


class SankashaAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'name')  # 一覧に出したい項目
    list_display_links = ('id', 'event', 'name',)  # 修正リンクでクリックできる項目


admin.site.register(Sankasha, SankashaAdmin)


class SankaNichijiAdmin(admin.ModelAdmin):
    list_display = ('id', 'sankasha', 'event_kouho_nichiji', 'sanka_kahi',)  # 一覧に出したい項目
    list_display_links = ('id', 'sankasha', 'event_kouho_nichiji', 'sanka_kahi',)  # 修正リンクでクリックできる項目


admin.site.register(SankaNichiji, SankaNichijiAdmin)


class EventKouhoNichijiAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'kouho_nichiji',)  # 一覧に出したい項目
    list_display_links = ('id', 'event', 'kouho_nichiji',)  # 修正リンクでクリックできる項目


admin.site.register(EventKouhoNichiji, EventKouhoNichijiAdmin)

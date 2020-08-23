from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from home import helpers
from home.forms import EventForm
from home.models import Event, EventKouhoNichiji


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# トップページ遷移関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def index(request):  # 追加
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/top.html')


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント追加関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_add(request):
    """イベントの追加"""
    form = EventForm(request.POST)  # POST された request データからフォームを作成
    if form.is_valid():  # フォームのバリデーション
        with transaction.atomic():
            # ===================================================
            # 保存対象モデルデータ作成
            # ※Eventはフォームデータから作成する。
            # ===================================================
            event = form.save(commit=False)

            # ===================================================
            # 保存対象データ設定処理
            # ===================================================
            # ------------------------
            # Event
            # ------------------------
            # 暗証番号
            # ※暗号化して保存する。
            encoded_anshou_num = helpers.encode_anshou_num(form.cleaned_data['anshou_num'])
            event.anshou_num = encoded_anshou_num

            # ===================================================
            # 保存処理 #1
            # ===================================================
            event.save()

            # ===================================================
            # ここから保存処理#2用処理
            # ===================================================

            # ===================================================
            # イベント日時候補レコード作成処理
            # 　画面の「イベント日時候補」※に入力された文字列を取得、処理して保存対象データを加工・作成する。
            # 　※改行コード区切り
            # ===================================================
            event_datetime_kouhos = helpers.get_event_datetime_kouhos(form.cleaned_data['event_datetime_kouho'])

            # ===================================================
            # 保存対象データ設定処理
            # ===================================================
            # ------------------------
            # Event
            # ------------------------
            # スケジュール更新ページID
            schedule_update_id = helpers.create_schedule_update_id(event.id)
            event.schedule_update_id = schedule_update_id

            # ------------------------
            # EventKouhoNichiji
            # ------------------------
            eventKouhoNichijis = [EventKouhoNichiji(event=event, kouho_nichiji=event_datetime_kouho) for event_datetime_kouho in event_datetime_kouhos]

            # ===================================================
            # 保存処理 #2
            # ===================================================
            EventKouhoNichiji.objects.bulk_create(eventKouhoNichijis)
            event.save()

            # ===================================================
            # 次画面遷移
            # ===================================================
        return render(request,
                      'home/schedule_fill.html',  # 使用するテンプレート
                      dict(form=form, event_id=event.id))  # テンプレートに渡すデータ

    return render(request, 'home/top.html', dict(form=form))
    # return redirect('home:index')


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# スケジュール更新関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def schedule_fill(request):
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/event_list.html',  # 使用するテンプレート
                  {'events': events})  # テンプレートに渡すデータ


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント一覧化関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_list(request):
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/event_list.html',  # 使用するテンプレート
                  {'events': events})  # テンプレートに渡すデータ


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント追加・編集関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_edit(request, event_id=None):
    """イベントの編集"""
    # return HttpResponse('書籍の編集')
    if event_id:  # event_id が指定されている (修正時)
        event = get_object_or_404(Event, pk=event_id)
    else:  # event_id が指定されていない (追加時)
        event = Event()

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)  # POST された request データからフォームを作成
        if form.is_valid():  # フォームのバリデーション
            event = form.save(commit=False)
            event.save()
            return redirect('home:event_list')
    else:  # GET の時
        form = EventForm(instance=event)  # event インスタンスからフォームを作成

    return render(request, 'home/event_edit.html', dict(form=form, event_id=event_id))


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント削除関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_del(request, event_id):
    """イベントの削除"""
    # return HttpResponse('イベントの削除')
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('home:event_list')

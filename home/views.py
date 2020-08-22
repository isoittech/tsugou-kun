from django.shortcuts import render, get_object_or_404, redirect

from home.forms import EventForm
from home.models import Event


def index(request):  # 追加
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/top.html',  # 使用するテンプレート
                  {'events': events})  # テンプレートに渡すデータ


def event_list(request):
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/event_list.html',  # 使用するテンプレート
                  {'events': events})  # テンプレートに渡すデータ


def event_edit(request, event_id=None):
    """書籍の編集"""
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


def event_del(request, event_id):
    """イベントの削除"""
    # return HttpResponse('イベントの削除')
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('home:event_list')

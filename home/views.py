# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# ■views.py
# TODO ロギング→デコレータを利用する。
# http://shimada-k.hateblo.jp/entry/2019/12/09/125244
# TODO 例外ハンドラ→これもデコレータを実装する。エラーが発生したらerror.htmlへ遷移させる。
# https://qiita.com/homines22/items/dccae65fa3434641b995
# TODO イベント日時候補テーブルに関する変数名・表記揺れ
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
import json
from urllib.parse import urlencode

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from home import helpers, constants
from home.forms import EventForm, EventSankakahiForm, EventEditForm
from home.helpers import get_event_datetime_dict
from home.models import Event, EventKouhoNichiji, SankaNichiji, Sankasha


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# トップページ遷移関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def index(request):  # 追加
    """イベントの一覧"""
    events = Event.objects.all().order_by('id')
    return render(request,
                  'home/top.html')


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント追加・編集関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_add(request):
    """
    イベントの追加・編集
    """

    # ===================================================
    # パラメータ取得
    # ===================================================
    # ------------------------
    # EventテーブルID
    # ------------------------
    schedule_update_id = request.POST.get('key')
    # イベント追加画面（新規登録）から来た（True）のか、編集画面から来たのか
    is_event_add = schedule_update_id == None
    if not is_event_add:
        event_id = helpers.decode_from_schedule_update_id(schedule_update_id)

    # ------------------------
    # 削除対象のイベント日時候補ID調査
    # ------------------------
    del_event_datetime_kouho_id_list = {}
    if not is_event_add:
        for key in request.POST:
            if 'del_eve_dt_kouho_id_' in key:
                del_event_datetime_kouho_id_list[key] = request.POST[key]

    # ===================================================
    # Formオブジェクト作成
    # ===================================================
    if is_event_add:
        # イベント追加画面（新規登録）から来たとき
        form = EventForm(request.POST)
    else:
        # イベント編集画面から来たとき
        event = Event.objects.get(pk=event_id)
        event_datetime_dict = get_event_datetime_dict(event)
        # パラメータ3,4は、チェックボックス（表示とチェック状態）を準備するために使う
        form = EventEditForm(
            request.POST,  # 1.
            key=schedule_update_id,  # 2.
            event_datetime_dict=event_datetime_dict,  # 3. 削除対象候補チェックボックス全量
            del_event_datetime_kouho_id_list=del_event_datetime_kouho_id_list  # 4. 前画面でのチェック済チェックボックス
        )

    if form.is_valid():  # フォームのバリデーション
        with transaction.atomic():
            # ===================================================
            # 保存対象モデルデータ作成
            # ===================================================
            event = form.save(commit=False)

            # ===================================================
            # 保存処理 #1
            # ※2つに分けている理由：新規登録の場合、一旦保存しないとPKが採番されないため。
            # ===================================================
            if is_event_add:
                # スケジュール更新ページIDが渡されなかった場合のみ保存する
                event.save()
            else:
                # スケジュール更新ページIDが渡された場合は既存レコードを保存対象とする
                event.id = event_id

            # ===================================================
            # イベント日時候補レコード削除
            # ※編集画面にて削除を選択された日時がある場合の処理
            # ===================================================
            if not is_event_add:
                for del_id in del_event_datetime_kouho_id_list.values():
                    # Deleteクエリが対象数分繰り替えされるが少数であると考えられるのでこれで削除する
                    EventKouhoNichiji.objects.filter(id=del_id).delete()

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
            # イベント
            # ------------------------
            # スケジュール更新ページID
            schedule_update_id = helpers.create_schedule_update_id(event.id)
            event.schedule_update_id = schedule_update_id

            # ------------------------
            # イベント日時候補
            # ------------------------
            eventKouhoNichijis = []
            for event_datetime_kouho in event_datetime_kouhos:
                if event_datetime_kouho != '':
                    eventKouhoNichijis.append(EventKouhoNichiji(event=event, kouho_nichiji=event_datetime_kouho))

            # ===================================================
            # 保存処理 #2
            # ===================================================
            if len(eventKouhoNichijis) != 0: EventKouhoNichiji.objects.bulk_create(eventKouhoNichijis)
            event.save()

        # ===================================================
        # 次画面遷移
        # ===================================================
        # ------------------------
        # リダイレクト先のパスを取得する
        # ------------------------
        redirect_url = reverse('home:notify_event_add_completed')

        # ------------------------
        # パラメータのdictをurlencodeする
        # ------------------------
        parameters = urlencode({'key': schedule_update_id})

        # ------------------------
        # URLにパラメータを付与して遷移する
        # ------------------------
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

    # ===================================================
    # フォームバリデーションエラー時の次画面遷移
    # ===================================================
    if is_event_add:
        # イベント新規登録画面（TOP画面）へ遷移
        return render(request, 'home/top.html', dict(form=form))
    else:
        # イベント編集画面へ遷移
        params = dict(form=form)
        return render(request, 'home/event_edit.html', params)


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント追加完了ページ遷移関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def notify_event_add_completed(request):
    """イベント追加完了"""
    # ------------------------
    # スケジュール編集URLを取得する
    # ------------------------
    parameters = urlencode({'key': request.GET.get('key')})
    schedule_fill_url = reverse('home:event_kouho')
    schedule_fill_url = "{}://{}{}?{}".format(request.scheme, request.get_host(), schedule_fill_url, parameters)

    return render(request,
                  'home/notify_event_add_completed.html',  # 使用するテンプレート
                  {'schedule_fill_url': schedule_fill_url})  # テンプレートに渡すデータ


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# イベント日時候補表示関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_kouho_print(request):
    """各個人のスケジュール更新画面表示"""

    # ===================================================
    # パラメータ取得
    # ===================================================
    # ------------------------
    # スケジュール更新ページID
    # ------------------------
    schedule_update_id = request.GET.get('key')
    event_id = helpers.decode_from_schedule_update_id(schedule_update_id)

    # ===================================================
    # DBデータ取得
    # ===================================================
    # ------------------------
    # イベントレコード
    # ------------------------
    event = Event.objects.get(pk=event_id)

    # ------------------------
    # イベント日時候補レコード
    # ------------------------
    result = EventKouhoNichiji.objects.filter(event=event)
    event_kouho_nichiji_list = [entry for entry in result]

    # ------------------------
    # 当該イベント参加者ｘ参加日時(SankaNichiji)の組み合わせのレコード
    # データ形式：下記形式の辞書（二重）
    # {参加者ID: {"name": 参加者名, "comment": コメント, 参加日時1のイベント候補日時のID: 参加可否（○or△or✕）, 参加日時2のイベント候補日時のID: 参加可否, …}
    # ※Sankashaレコードが取得できない場合（＝誰も参加可否を投入していない場合）、辞書は空となる。
    # ------------------------
    event_sankasha_sankakahi_dict_dict = {}
    try:
        for sankasha in Sankasha.objects.prefetch_related("sankasha_sanka_nichiji_set").filter(event=event):
            sankasha_dict = {}  # 内側の辞書
            sankasha_dict['name'] = sankasha.name
            sankasha_dict['comment'] = sankasha.comment
            for sankanichiji in sankasha.sankasha_sanka_nichiji_set.all():
                sankasha_dict[sankanichiji.event_kouho_nichiji.id] = sankanichiji.sanka_kahi
            event_sankasha_sankakahi_dict_dict[sankasha.id] = sankasha_dict
    except Sankasha.DoesNotExist:
        pass

    # ------------------------
    # イベント日時候補データの1レコードごとの参加日時データ
    # データ形式：下記形式の辞書＆配列
    # {イベント日時候補テーブルID: [参加日時文字列, 参加者1の当時刻の回答レコード, 参加者2の当時刻の回答レコード,…]}
    # ※SankaNichijiレコードが取得できない場合（＝誰も参加可否を投入していない場合）、下記内容となる。
    #   {イベント日時候補テーブルID#1: [参加日時文字列], イベント日時候補テーブルID#2: [参加日時文字列], …}
    # ------------------------
    event_sanka_list_dict = {}
    for event_kouho_nichiji in event_kouho_nichiji_list:
        sanka_nichiji_list_of_a_datetime = SankaNichiji.objects.select_related('event_kouho_nichiji').filter(event_kouho_nichiji=event_kouho_nichiji)
        sanka_nichiji_list_of_a_datetime = [entry for entry in sanka_nichiji_list_of_a_datetime]
        if len(sanka_nichiji_list_of_a_datetime) == 0:
            sanka_nichiji_list_of_a_datetime = [event_kouho_nichiji.kouho_nichiji]
        else:
            sanka_nichiji_list_of_a_datetime.insert(0, event_kouho_nichiji.kouho_nichiji)
        event_sanka_list_dict[event_kouho_nichiji.id] = sanka_nichiji_list_of_a_datetime

    # ===================================================
    # 集計処理
    # ===================================================
    # ------------------------
    # イベント日時候補ごとの○・△・✕の数データ
    # データ形式：下記形式の辞書＆配列
    # {イベント日時候補テーブルID: {event_nichizi_kouho_id: イベント日時候補テーブルID, nichiji: 参加日時文字列, maru: ○の数, sankaku: △の数, batsu: ✕の数}}
    # ※誰も参加可否を投入していない場合、下記内容となる。
    #   {イベント日時候補テーブルID: {event_nichizi_kouho_id: イベント日時候補テーブルID, nichiji: 参加日時文字列, maru: 0, sankaku: 0, batsu: 0}}
    # ------------------------
    event_sanka_shuukei_dict_dict = {}
    for event_kouho_nichiji_id, event_sanka_list in event_sanka_list_dict.items():  # イベント日時分のループ
        shuukei_data = {
            'event_nichizi_kouho_id': event_kouho_nichiji_id,
            'nichiji': event_sanka_list[0],  # event_sanka_listの要素0には参加日時文字列が格納されている
            'maru': 0, 'sankaku': 0, 'batsu': 0
        }
        for i in range(1, len(event_sanka_list)):  # 参加者数分のループ
            event_sanka = event_sanka_list[i]
            # sanka_kahiの取りうる値：1（○）、2（△）、3（✕）
            if event_sanka.sanka_kahi == constants.SANKA_MARU:
                shuukei_data['maru'] += 1
            elif event_sanka.sanka_kahi == constants.SANKA_SANKAKU:
                shuukei_data['sankaku'] += 1
            elif event_sanka.sanka_kahi == constants.SANKA_BATSU:
                shuukei_data['batsu'] += 1
        event_sanka_shuukei_dict_dict[event_kouho_nichiji_id] = shuukei_data

    # ===================================================
    # 描画用データ作成処理
    # ===================================================
    # ------------------------
    # (1)
    # イベント日時候補ごとの'参加'・'欠席'・'微妙'の数データ＋参加者の参加可否詳細
    # データ形式：下記形式の配列＆辞書
    # [{nichiji: 参加日時文字列, maru: ○の数, sankaku: △の数, batsu:✕の数, 参加者1の名前: 参加者1の参加可否, 参加者2の名前: 参加者2の参加可否, …]}
    # ※(2)(3)と一緒に作る
    # ------------------------
    # ------------------------
    # (2)
    # イベント参加者名配列
    # データ形式：下記形式の辞書
    # [参加者1名前: '参加者1ID,参加者1名前,参加者1のコメント,参加日時1のイベント候補日時のID,参加者1の参加日時1の参加可否,参加日時2のイベント候補日時のID,参加者1の参加日時2の参加可否,…'
    #  ,参加者2名前: '参加者2ID,参加者2名前,参加者2のコメント,参加日時1のイベント候補日時のID,参加者2の参加日時1の参加可否,参加日時2のイベント候補日時のID,参加者2の参加日時2の参加可否,…'
    #  ,…]
    # ※参加可否の編集元データとして使用される。イベント参加者名をクリックすると、このデータがjQueryにより、編集フォームに反映される。
    # ※(1)(3)と一緒に作る
    # ------------------------
    # ------------------------
    # (3)
    # イベント参加者コメント配列
    # データ形式：下記形式の配列
    # [参加者1コメント, 参加者2コメント, …]
    # ※(1)(2)と一緒に作る
    # ------------------------

    # 作成するデータの入れ物
    # ※誰も参加可否を投入していない場合(2)(3)は空配列となる。
    # (1)
    event_sanka_table_dict_list = []
    # (2)
    event_sankasha_dict = {}
    # (3)
    event_sankasha_comments = []

    # 下記形式の変数event_sankasha_sankakahi_dict_dictをもとに処理する
    # {参加者ID: {"name": 参加者名, "comment": コメント, 参加日時1のイベント候補日時のID: 参加可否（○or△or✕）, 参加日時2のイベント候補日時のID: 参加可否, …}
    for sankasha_id, event_sankasha_sankakahi_dict in event_sankasha_sankakahi_dict_dict.items():  # イベント参加者分のループ
        name = event_sankasha_sankakahi_dict['name']
        event_sankasha_dict[name] = str(sankasha_id) + ',' + name + ',' + event_sankasha_sankakahi_dict['comment']
        event_sankasha_comments.append(event_sankasha_sankakahi_dict['comment'])
        for key, event_sankasha_sankakahi in event_sankasha_sankakahi_dict.items():  # 辞書要素数分のループ
            if not key in ['name', 'comment']:
                # {nichiji: 参加日時文字列, maru: ○の数, sankaku: △の数, batsu: ✕の数} のデータ取得
                event_sanka_shuukei_dict = event_sanka_shuukei_dict_dict[key]
                # 上記に、参加者Xの名前: 参加者Xの参加可否を追加
                event_sanka_shuukei_dict[name] = event_sankasha_sankakahi
                # (2)のデータ作成
                event_sankasha_dict[name] = event_sankasha_dict[name] + ',' + str(key) + ',' + str(event_sankasha_sankakahi)

    # ここまでの処理で、event_sanka_shuukei_dict_dictの形式は下記：
    # {イベント日時候補テーブルID: {event_nichizi_kouho_id: イベント日時候補テーブルID, nichiji: 参加日時文字列, maru: ○の数, sankaku: △の数, batsu: ✕の数, 参加者1の名前: 参加者1の参加可否, 参加者2の名前: 参加者2の参加可否, …}}
    event_sanka_table_dict_list.extend(event_sanka_shuukei_dict_dict.values())

    # ------------------------
    # 描画用データ作成処理(4)
    # イベント参加者記入用radioフォーム描画用の配列
    # データ形式：下記形式辞書の配列
    # {nichiji: イベント日時候補文字列（例：X月Y日Z時）, event_nichizi_kouho_id: イベント日時候補テーブルID, selected_value: 選択肢に対応する値（1,2,3）}
    # ------------------------
    event_sanka_fill_table_dict_list = []
    for event_kouho_nichiji in event_kouho_nichiji_list:
        event_sanka_fill_table_dict = {}
        event_sanka_fill_table_dict['nichiji'] = event_kouho_nichiji.kouho_nichiji
        event_sanka_fill_table_dict['event_nichizi_kouho_id'] = event_kouho_nichiji.id
        event_sanka_fill_table_dict['selected_value'] = 0
        event_sanka_fill_table_dict_list.append(event_sanka_fill_table_dict)

    # ===================================================
    # 次画面遷移
    # ===================================================
    params = {  # テンプレートに渡すデータ
        'event_name': event.name,
        'event_memo': event.memo,
        'event_sanka_table_dict_list': event_sanka_table_dict_list,
        'event_sankasha_dict': event_sankasha_dict,
        'event_sankasha_comments': event_sankasha_comments,
        'schedule_update_id': schedule_update_id,  # スケジュール更新ページID
        'event_sanka_fill_table_dict_list': event_sanka_fill_table_dict_list
    }

    # 各個人のスケジュール更新画面で入力・Submit後、エラーが発生して、
    # 当該画面へ遷移した時に描画できるよう、この関数で準備したパラメータをそのまま渡す（jsonにして）
    jsoned_params = json.dumps(params)
    params['jsoned_params'] = jsoned_params

    return render(
        request,
        'home/event_kouho.html',  # 使用するテンプレート
        params
    )


# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# スケジュール更新関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def schedule_fill(request):
    """各個人のスケジュール更新"""

    # ===================================================
    # パラメータ取得
    # ===================================================
    # ------------------------
    # スケジュール更新ページID
    # ------------------------
    schedule_update_id = request.POST.get('key')
    event_id = helpers.decode_from_schedule_update_id(schedule_update_id)
    sankasha_id = request.POST.get('sankasha_id')

    # ===================================================
    # DBデータ取得
    # ===================================================
    # ===================================================
    # イベントテーブル
    # ===================================================
    event = Event.objects.get(pk=event_id)

    # ------------------------
    # イベント候補日時テーブル
    # ------------------------
    event_kouho_nichiji_list = EventKouhoNichiji.objects.filter(event=event)
    event_kouho_nichiji_list = [entry for entry in event_kouho_nichiji_list]

    # ===================================================
    # バリデーション・保存処理
    # ===================================================
    form = EventSankakahiForm(request.POST)  # POST された request データからフォームを作成
    if form.is_valid():  # フォームのバリデーション
        with transaction.atomic():

            # ===================================================
            # 保存対象モデルデータ作成
            # ===================================================
            sankasha = form.save(commit=False)
            if sankasha_id != '': sankasha.id = sankasha_id
            sankasha.event = event

            # ===================================================
            # 保存処理 #1
            # ===================================================
            sankasha.save()
            # 更新時における古いデータを消す。更新対象データを特定する処理が面倒なので、
            SankaNichiji.objects.filter(sankasha=sankasha).delete()

            # ===================================================
            # ここから保存処理#2用処理
            # ===================================================

            # ===================================================
            # 参加日時レコードをイベント候補日時レコード数分作成
            # ===================================================
            # ------------------------
            # イベント候補日時テーブルレコードリストでループ
            # ・参加日時レコード生成
            # ・POSTデータから参加可否の値を取得、レコードに設定
            #   ※もし回答していない日時があればその日時は0（未入力）とする。
            # ・イベント候補日時テーブルレコードと参加者テーブルレコードもレコードに設定
            # ------------------------
            sanka_nichiji_record_list = []
            for event_kouho_nichiji in event_kouho_nichiji_list:
                sanka_nichiji_record = SankaNichiji()
                sanka_nichiji_record.sankasha = sankasha
                sanka_nichiji_record.event_kouho_nichiji = event_kouho_nichiji
                sanka_kahi_key = 'event_nichizi_kouho_id_' + str(event_kouho_nichiji.id)
                sanka_nichiji_record.sanka_kahi = request.POST[sanka_kahi_key] if sanka_kahi_key in request.POST else constants.SANKA_MINYUURYOKU
                sanka_nichiji_record_list.append(sanka_nichiji_record)

            # ===================================================
            # 保存処理 #2
            # ===================================================
            # ------------------------
            # SankaNichiji
            # ------------------------
            SankaNichiji.objects.bulk_create(sanka_nichiji_record_list)

        # ===================================================
        # 次画面遷移
        # ===================================================
        # リダイレクト先のパスを取得する
        redirect_url = reverse('home:event_kouho')

        # パラメータのdictをurlencodeする
        parameters = urlencode({'key': schedule_update_id})

        # URLにパラメータを付与して遷移する
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

    # ===================================================
    # フォームバリデーションエラー時の次画面遷移用パラメータ作成
    # ===================================================
    # ------------------------
    # イベント参加者記入用radioフォーム描画用の配列
    # データ形式：下記形式辞書の配列
    # {nichiji: イベント日時候補文字列（例：X月Y日Z時）, event_nichizi_kouho_id: イベント日時候補テーブルID, selected_value: 選択肢に対応する値（1,2,3）}
    # ------------------------
    event_sanka_fill_table_dict_list = []
    for event_kouho_nichiji in event_kouho_nichiji_list:
        event_sanka_fill_table_dict = {}
        event_sanka_fill_table_dict['nichiji'] = event_kouho_nichiji.kouho_nichiji
        event_sanka_fill_table_dict['event_nichizi_kouho_id'] = event_kouho_nichiji.id
        event_sanka_fill_table_dict['selected_value'] = form.data['event_nichizi_kouho_id_' + str(event_kouho_nichiji.id)]
        event_sanka_fill_table_dict_list.append(event_sanka_fill_table_dict)

    # ------------------------
    # 他
    # ------------------------
    params = dict(form=form)
    params['schedule_update_id'] = schedule_update_id
    params['jsoned_params'] = request.POST['jsoned_params']  # そのまま引き継ぐ
    params['sanka_kahi_area_open'] = 'true'
    initial_params = json.loads(request.POST['jsoned_params'])  # 当該画面に元々表示されていた画面データ
    params.update(initial_params)
    params['event_sanka_fill_table_dict_list'] = event_sanka_fill_table_dict_list

    return render(request, 'home/event_kouho.html', params)


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
# イベント追加・編集画面表示準備 関数
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_edit_prepare(request):
    """イベント編集画面"""

    # ===================================================
    # パラメータ取得
    # ===================================================
    # ------------------------
    # スケジュール更新ページID
    # ------------------------
    schedule_update_id = request.GET.get('key')
    event_id = helpers.decode_from_schedule_update_id(schedule_update_id)

    # ===================================================
    # DBデータ取得
    # ===================================================
    # ------------------------
    # イベントレコード
    # ------------------------
    event = Event.objects.get(pk=event_id)

    # ===================================================
    # テンプレートへ渡すパラメータ準備
    # ===================================================
    # ------------------------
    # イベント日時候補辞書
    # ------------------------
    event_datetime_dict = get_event_datetime_dict(event)
    # ------------------------
    # 入力フォーム初期値準備1（単純に渡せるもの）
    # ------------------------
    data = {
        'name': event.name,
        'memo': event.memo,
        'key': schedule_update_id,
        'event_datetime_kouho': '',
    }

    # ------------------------
    # 入力フォーム初期値準備2（単純に渡せないもの）
    # ------------------------
    # パラメータ3,4は、チェックボックス（表示とチェック状態）を準備するために使う
    form = EventEditForm(
        data,  # 1.
        key=schedule_update_id,  # 2.
        event_datetime_dict=event_datetime_dict,  # 3. 削除対象候補チェックボックス全量
        del_event_datetime_kouho_id_list={}  # 4. 前画面でのチェック済チェックボックス
    )

    # ===================================================
    # 遷移
    # ===================================================
    params = dict(form=form)
    params['event_datetime_dict'] = event_datetime_dict
    return render(request, 'home/event_edit.html', params)

    # ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    # イベント削除関数
    # ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
def event_del(request, event_id):
    """イベントの削除"""
    # return HttpResponse('イベントの削除')
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    return redirect('home:event_list')

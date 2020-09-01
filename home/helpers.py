import base64
import collections
import datetime
import os
import re
from urllib.parse import urlencode

from django.shortcuts import render
from django.urls import reverse

from home.models import EventKouhoNichiji, Event

CRYPT_SEED_FOR_ID = 'CRYPT_SEED_FOR_ID'
CRYPT_SEED_FOR_ANSHOU_NUM = 'CRYPT_SEED_FOR_ANSHOU_NUM'
LINE_FEED_CD = os.linesep
COOKIE_EXPIRE_SECONDS = 365 * 24 * 60 * 60


def encode(encode_key, target_str):
    enc = []
    for i in range(len(target_str)):
        encode_key_c = encode_key[i % len(encode_key)]
        enc_c = chr((ord(target_str[i]) + ord(encode_key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(encode_key, encoded_str):
    dec = []
    encoded_str = base64.urlsafe_b64decode(encoded_str).decode()
    for i in range(len(encoded_str)):
        encode_key_c = encode_key[i % len(encode_key)]
        dec_c = chr((256 + ord(encoded_str[i]) - ord(encode_key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def create_schedule_update_id(schedule_update_id_seed):
    try:
        return encode(CRYPT_SEED_FOR_ID, '<crypt>' + str(schedule_update_id_seed) + '</crypt>')
    except Exception as e:
        print('[ERROR] create_schedule_update_idでエラー。引数:{}'.format(schedule_update_id_seed))
        raise e


def encode_anshou_num(anshou_num):
    try:
        return encode(CRYPT_SEED_FOR_ANSHOU_NUM, '<crypt>' + str(anshou_num) + '</crypt>')
    except Exception as e:
        print('[ERROR] encode_anshou_numでエラー。引数:{}'.format(anshou_num))
        raise e


def decode_from_schedule_update_id(schedule_update_id):
    try:
        decoded = decode(CRYPT_SEED_FOR_ID, schedule_update_id)
        match = re.findall(r'<crypt>(.*)</crypt>', decoded)
        return match[0]
    except Exception as e:
        print('[ERROR] decode_from_schedule_update_idでエラー。引数:{}'.format(schedule_update_id))
        raise e


def decode_from_encoded_anshou_num(encoded_anshou_num):
    try:
        decoded = decode(CRYPT_SEED_FOR_ANSHOU_NUM, encoded_anshou_num)
        match = re.findall(r'<crypt>(.*)</crypt>', decoded)
        return match[0]
    except Exception as e:
        print('[ERROR] decode_from_encoded_anshou_numでエラー。引数:{}'.format(encoded_anshou_num))
        raise e


def get_event_datetime_kouhos(event_datetime_kouho_str):
    try:
        event_datetime_kouho_str_list = event_datetime_kouho_str.split(LINE_FEED_CD)
        return list(filter(lambda str: str != '', event_datetime_kouho_str_list))
    except Exception as e:
        print('[ERROR] get_event_datetime_kouhosでエラー。引数:{}'.format(event_datetime_kouho_str))
        raise e


def get_event_datetime_dict(event):
    """
    イベント日時候補辞書を返却する。
    :param event: イベントテーブル
    :return: 下記形式のイベント日時候補辞書
        key: イベント日時候補テーブルID
        value: イベント日時候補文字列（X月Y日Z時等）
    """
    # ------------------------
    # イベント日時候補レコード
    # ------------------------
    result = EventKouhoNichiji.objects.filter(event=event)
    event_kouho_nichiji_list = [entry for entry in result]

    # ------------------------
    # イベント日時候補辞書
    # ------------------------
    event_datetime_dict = {}
    for event_kouho_nichiji in event_kouho_nichiji_list:
        event_datetime_dict[event_kouho_nichiji.id] = event_kouho_nichiji.kouho_nichiji

    return event_datetime_dict


def set_cookie(response, key, value, max_age=COOKIE_EXPIRE_SECONDS):
    """
    Cookieに情報を詰める
    :param response:
    :param key:
    :param value:
    :param max_age:
    :return:
    """
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def render_with_histories(request, template_name, context=None, event_id=None, content_type=None, status=None, using=None):
    """
    Cookieの設定および、event_historiesをレスポンスに設定して返却する

    -----------
    event_historiesの形式：
    -----------
    [{schedule_fill_url: スケジュール更新URL, event_name: イベント名, event_kouho_nichiji_list: [イベント候補日時1文字列, 日時2文字列, ...]}, ...]

    -----------
    処理：
    -----------
    Cookieにevent_id（N個）のエンコ済のCSVを設定する
    1. Cookieからキー'schedule_update_id_*'で値を検索し、ヒットしたものを要素群とするschedule_update_id_dictを取得する。
    2. 関数パラメータevent_idがある場合は、schedule_update_id_dictから関数パラメータのエンコ済event_idと同じ値を削除する。
    3. 関数パラメータevent_idがある場合は、schedule_update_id_dictの0番目に関数パラメータのエンコ済event_idを入れる。
       ※2,3の処理で順番を入れ替えている。
         関数パラメータに渡されたIDのイベントを「最も最近になって見たイベント」という意味付けのため。
    4. schedule_update_id_dictをN個にする。N+1個目以降は削除する（表示対象から外す）。
    5. 返却用Listを作成後、schedule_update_id_dict（key: schedule_update_id_XX,  value: エンコ済event_id）の分、ループを回し、下記を実施する。
      5.1. 返却用Dict event_dictを新規作成する。
      5.2. EventのID（エンコ済event_idをデコードして）でEventレコードを取得する。
      5.3. 取得したEventレコードをもとに算出・取得したschedule_fill_url、event_nameをevent_dictに設定する。
      5.4. 取得したEventレコードをもとにイベント日時候補レコードリストを取得、日時文字列をevent_kouho_nichiji_listにaddしてevent_dictに設定する。
      5.5. event_dictを返却用Listに追加する。
    6. 関数パラメータevent_idがある場合は、エンコ済event_idでCookieを設定する。

    """

    # ------------------------
    # 処理1
    # ------------------------
    schedule_update_id_dict = collections.OrderedDict()
    for key, value in request.COOKIES.items():  # iter on both keys and values
        if key.startswith('schedule_update_id_'):
            schedule_update_id_dict[key] = value  # valueはエンコ済event_id

    # ------------------------
    # 処理2,3
    # ------------------------
    if event_id:
        enc_schedule_update_id = create_schedule_update_id(event_id)
        _key = 'schedule_update_id_' + str(event_id)
        if _key in schedule_update_id_dict: schedule_update_id_dict.pop(_key)

        l = list(schedule_update_id_dict.items())
        l.insert(0, ('schedule_update_id_' + str(event_id), enc_schedule_update_id))
        schedule_update_id_dict = collections.OrderedDict(l)

    # ------------------------
    # 処理4
    # ------------------------
    _tmp = {}
    for idx, key in enumerate(schedule_update_id_dict):
        if idx == 5: break
        _tmp[key] = schedule_update_id_dict[key]
    schedule_update_id_dict = _tmp

    # ------------------------
    # 処理5
    # ------------------------
    event_histories = []
    for schedule_update_id_XX, enc_event_id in schedule_update_id_dict.items():
        event_dict = {}
        each_event_id = decode_from_schedule_update_id(enc_event_id)
        event = Event.objects.get(pk=each_event_id)
        parameters = urlencode({'key': enc_event_id})
        schedule_fill_url = reverse('home:event_kouho')
        schedule_fill_url = "{}://{}{}?{}".format(request.scheme, request.get_host(), schedule_fill_url, parameters)
        event_dict['schedule_fill_url'] = schedule_fill_url
        event_dict['event_name'] = event.name
        event_dict['event_kouho_nichiji_list'] = get_event_datetime_dict(event).values()
        event_histories.append(event_dict)

    if len(event_histories) != 0:
        if context == None: context = {}
        context['event_histories'] = event_histories

    # ------------------------
    # 処理6
    # ------------------------
    response = render(request, template_name, context, content_type, status, using)
    if event_id:
        enc_schedule_update_id = create_schedule_update_id(event_id)
        set_cookie(response, 'schedule_update_id_' + str(event_id), enc_schedule_update_id)

    return response

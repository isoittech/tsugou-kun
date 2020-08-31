import base64
import os
import re

from home.models import EventKouhoNichiji

CRYPT_SEED_FOR_ID = 'CRYPT_SEED_FOR_ID'
CRYPT_SEED_FOR_ANSHOU_NUM = 'CRYPT_SEED_FOR_ANSHOU_NUM'
LINE_FEED_CD = os.linesep


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

    # ===================================================
    # イベント日時候補辞書
    # ===================================================
    event_datetime_dict = {}
    for event_kouho_nichiji in event_kouho_nichiji_list:
        event_datetime_dict[event_kouho_nichiji.id] = event_kouho_nichiji.kouho_nichiji

    return event_datetime_dict

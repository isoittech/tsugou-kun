from django.core.exceptions import ValidationError
from django.db import models

def only_intger(value):
    if value.isdigit() == False:
        raise ValidationError('暗証番号は4桁の数字を入力して下さい。')


class Event(models.Model):
    """イベント"""
    name = models.CharField('イベント名', max_length=255)
    memo = models.CharField('メモ', max_length=255, blank=True)
    schedule_update_id = models.CharField('スケジュール更新ID', max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'イベント情報'
        verbose_name_plural = verbose_name


class EventKouhoNichiji(models.Model):
    """イベント候補日時"""
    event = models.ForeignKey(Event, verbose_name='イベント', related_name='event_kouho_nichiji_set', on_delete=models.CASCADE)
    kouho_nichiji = models.CharField('候補日時', max_length=255)

    def __str__(self):
        return self.kouho_nichiji

    class Meta:
        verbose_name = 'イベント候補日時情報'
        verbose_name_plural = verbose_name


class Sankasha(models.Model):
    """
    参加者
    ※参加者の情報を保持する
    """
    event = models.ForeignKey(Event, verbose_name='イベント', related_name='sankasha_set', on_delete=models.CASCADE)
    name = models.CharField('参加者名', max_length=255)
    comment = models.CharField('コメント', max_length=1024, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '参加者情報'
        verbose_name_plural = verbose_name


class SankaNichiji(models.Model):
    """
    参加日時
    ※参加者の各日時の参加可否を保持する
    """
    sankasha = models.ForeignKey(Sankasha, verbose_name='参加者', related_name='sankasha_sanka_nichiji_set', on_delete=models.CASCADE)
    event_kouho_nichiji = models.ForeignKey(EventKouhoNichiji, verbose_name='イベント候補日時', related_name='event_kouho_sanka_nichiji_set', on_delete=models.CASCADE)
    sanka_kahi = models.IntegerField('参加可否')

    def __str__(self):
        return self.sanka_kahi

    class Meta:
        verbose_name = '参加日時情報'
        verbose_name_plural = verbose_name

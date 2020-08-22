from django.db import models


class Event(models.Model):
    """イベント"""
    name = models.CharField('イベント名', max_length=255)
    memo = models.CharField('メモ', max_length=255, blank=True)

    def __str__(self):
        return self.name


class EventKouhoNichiji(models.Model):
    """イベント候補日時"""
    event = models.ForeignKey(Event, verbose_name='イベント', related_name='event_kouhobis', on_delete=models.CASCADE)
    kouho_nichiji = models.CharField('候補日時', max_length=255)

    def __str__(self):
        return self.kouho_nichiji


class Sankasha(models.Model):
    """参加者"""
    event = models.ForeignKey(Event, verbose_name='イベント', related_name='event_sankashas', on_delete=models.CASCADE)
    name = models.CharField('参加者名', max_length=255)

    def __str__(self):
        return self.name


class SankaNichiji(models.Model):
    """参加日時"""
    sankasha = models.ForeignKey(Sankasha, verbose_name='参加者', related_name='event_sanka_nichiji', on_delete=models.CASCADE)
    event_kouho_nichiji = models.ForeignKey(EventKouhoNichiji, verbose_name='イベント候補日時', related_name='event_sanka_nichiji', on_delete=models.CASCADE)
    sanka_kahi = models.IntegerField('参加可否')
    
    def __str__(self):
        return self.sanka_kahi

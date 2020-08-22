from django import forms
from django.forms import ModelForm

from home.models import Event


class EventForm(ModelForm):
    """イベントのフォーム"""

    def __init__(self, *args, **kwd):
        super(EventForm, self).__init__(*args, **kwd)
        self.fields["memo"].required = False

    class Meta:
        model = Event
        fields = ['name', 'memo']
        labels = {
            'name': '名前',
            'memo': 'メモ'
        }
        error_messages = {
            'name': {
                'required': '名前は必須です!'
            }
        }


class EventFormWithDate(EventForm):
    """
    イベントのフォーム（画面とのやりとり上、拡張したこちらを利用する）
    ※Formを拡張する理由：
　    　画面に表示する「イベント日時候補」を「イベント」エンティティにカラムにもたない。
  　  　画面から入力された「イベント候補日時」は改行付き文字列で、その1行1行が別エンティティ「イベント候補日時」のレコード1つになる。
    　　なので、一旦文字列を画面から取得したあと、viewsで加工する必要があるために分けている。
    """
    eventDatetimeKouho = forms.CharField

    class Meta(EventForm.Meta):
        fields = EventForm.Meta.fields
        labels = {
            'eventDatetimeKouho': 'イベント日時候補'
        }
        error_messages = {
            'eventDatetimeKouho': {
                'required': 'イベント日時候補は必須です!'
            }
        }

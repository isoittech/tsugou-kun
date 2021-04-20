from django import forms
from django.forms import CheckboxInput

from home.models import Event, Sankasha


class EventForm(forms.ModelForm):
    """
    イベントのフォーム
    """

    class Meta:
        model = Event
        fields = ('name', 'memo',)
        error_messages = {
            'name': {
                'required': 'イベント名は必須です!'
            }
        }

    event_datetime_kouho = forms.CharField(
        label='イベント日時候補',
        required=True,
        max_length=255,
        error_messages={'required': 'イベント日時候補は必須です!', }
    )


class EventEditForm(EventForm):
    """
    イベント編集のフォーム
    """
    event_datetime_kouho = forms.CharField(
        label='イベント日時候補',
        required=False,
        max_length=255,
    )

    key = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta(EventForm.Meta):
        fields = ('name', 'memo')

    def __init__(self, *args, **kwargs):
        # エンコ済イベントテーブルID
        key_value = kwargs.pop('key', None)
        # 削除対象候補チェックボックス全量
        event_datetime_dict = kwargs.pop('event_datetime_dict', None)
        # 前画面でのチェック済チェックボックス
        del_event_datetime_kouho_id_list = kwargs.pop('del_event_datetime_kouho_id_list', None)

        super(EventEditForm, self).__init__(*args, **kwargs)

        self.fields['key'].initial = key_value

        for eve_dt_kouho_id, nichiji_str in event_datetime_dict.items():
            # eve_dt_kouho_id: イベント日時候補テーブルID
            # nichiji_str: イベント日時候補文字列（X月Y日Z時等）
            field_name = 'del_eve_dt_kouho_id_' + str(eve_dt_kouho_id)
            attrs = {'value': eve_dt_kouho_id}
            if field_name in del_event_datetime_kouho_id_list:
                attrs['checked'] = 'checked'
            self.fields[field_name] = forms.BooleanField(label=nichiji_str, widget=CheckboxInput(attrs=attrs), required=False)


class EventSankakahiForm(forms.ModelForm):
    """
    イベント参加可否のフォーム
    """

    class Meta:
        model = Sankasha
        fields = ('name', 'comment',)
        error_messages = {
            'name': {
                'required': '名前は必須です!'
            }
        }

    sankasha_id = forms.HiddenInput()

    def add_sankakahi_form(self, name):
        self.fields[name] = forms.ChoiceField(
            required=False,
            initial=0
        )


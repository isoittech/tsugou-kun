from django import forms

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


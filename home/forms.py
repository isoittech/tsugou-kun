from django import forms

from home.models import Event


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

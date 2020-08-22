from django.forms import ModelForm

from home.models import Event


class EventForm(ModelForm):
    """イベントのフォーム"""

    class Meta:
        model = Event
        fields = ('name', 'memo')

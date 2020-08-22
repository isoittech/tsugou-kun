from django.forms import ModelForm

from home.models import Event


class EventForm(ModelForm):
    """書籍のフォーム"""

    class Meta:
        model = Event
        fields = ('name', 'memo')

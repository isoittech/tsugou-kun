from django import forms

from home.models import Event


class EventForm(forms.ModelForm):
    """
    イベントのフォーム（画面とのやりとり上、拡張したこちらを利用する）
    ※ModelFormではなくforms.Formを拡張する理由：
        画面に表示する「イベント日時候補」を「Event」エンティティにカラムにもたないが、
        カラムにもたないものをFormクラスにフィールドとして保持する方法が分からないため。
        → https://32imuf.com/django/form/ このサイトのやり方でよいかも。TODO.
  　  　※画面から入力された「イベント候補日時」は改行付き文字列で、その1行1行が別エンティティ「イベント候補日時」のレコード1つになる。
    　　　なので、一旦その改行付き文字列を画面から取得したあと、viewsで加工する必要がある。
    """

    class Meta:
        model = Event
        fields = ('name', 'memo', 'anshou_num',)
        error_messages = {
            'name': {
                'required': 'イベント名は必須です!'
            },
            'anshou_num': {
                'required': '暗証番号は必須です!後で編集するために必要です。',
                'min_length': '暗証番号は4桁の数字を入力して下さい。',
                'max_length': '暗証番号は4桁の数字を入力して下さい。'
            }
        }

    event_datetime_kouho = forms.CharField(
        label='イベント日時候補',
        required=True,
        max_length=255,
        error_messages={'required': 'イベント日時候補は必須です!', }
    )

    # name = forms.CharField(
    #     label='名前',
    #     max_length=255,
    #     required=True,
    #     error_messages={'required': 'イベント名は必須です!', }
    # )
    # memo = forms.CharField(
    #     label='メモ',
    #     max_length=255,
    #     required=False,
    # )
    # anshou_num = forms.CharField(
    #     label='暗証番号',
    #     min_length=4,
    #     max_length=4,
    #     required=True,
    #     error_messages={'required': '暗証番号は必須です!後で編集するために必要です。',
    #                     'min_length': '暗証番号は4桁の数字を入力して下さい。',
    #                     'max_length': '暗証番号は4桁の数字を入力して下さい。'
    #                     }
    # )
    # event_datetime_kouho = forms.CharField(
    #     label='イベント日時候補',
    #     max_length=255,
    #     required=True,
    #     error_messages={'required': 'イベント日時候補は必須です!', }
    # )

from django.http import HttpResponse  # 追加


def index(request):  # 追加
    return HttpResponse('初期構築')  # 追加

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from . import services
from .models import Event

def index(request):
    """
    入力用フロントエンド画面を返す
    """
    ## URLパタメータからtag_idを取得（例：/?tag_id=room1）
    tag_id = request.GET.get('tag_id', 'unknown_tag')
    return render(request, 'Core/index.html', {'tag_id': tag_id})


def event_list(request):
    """
    保存されたイベントを一覧表示する画面
    """
    events = Event.objects.all().order_by('-timestamp')
    return render(request, 'Core/list.html', {'events': events})


# API検証用
@csrf_exempt
def record_event(request):
    """
    NFCからのデータを受け取るAPI
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tag_id = data.get('tag_id')
            text = data.get('text')

            ## 動作確認のため、一旦printするだけにします
            print(f"記録完了: タグ = {tag_id}, テキスト = {text}")

            ## データベースに保存
            # Event.objects.create(tag_id = tag_id, text = text)

            ## 「タグID、入力テキスト、時間の文脈、心情、埋め込みベクトル」を取得
            services.process_nfc_event(tag_id = tag_id, text = text)

            ## イベントを受け取ったことを通知？
            # return JsonResponse({"status": "success", "event_id": event.id})
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status = 400)

    return JsonResponse({"status": "invalid method"}, status = 405)

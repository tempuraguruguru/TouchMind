from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
from . import services
from .models import Event

@login_required
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

            # ログインしているユーザーの情報を取得
            current_user = request.user

            ## 動作確認のため、一旦printするだけにします
            print(f"記録完了: タグ = {tag_id}, テキスト = {text}")

            ## データベースに保存
            # Event.objects.create(tag_id = tag_id, text = text)

            ## 「タグID、入力テキスト、時間の文脈、心情、埋め込みベクトル」を取得
            services.process_nfc_event(tag_id = tag_id, text = text, user = current_user)

            ## イベントを受け取ったことを通知？
            # return JsonResponse({"status": "success", "event_id": event.id})
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status = 400)

    return JsonResponse({"status": "invalid method"}, status = 405)


def signup(request):
    """
    新規ユーザー登録画面
    """
    if request.method == 'POST':
        # POSTされたデータでフォームを初期化
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # データベースに新しいユーザーを保存
            user = form.save()

            # 登録後、そのまま自動的にログインさせる
            login(request, user)

            # ログイン後は入力画面（トップページ）へリダイレクト
            return redirect('/')
    else:
        # GETアクセス時は空のフォームを表示
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def graph_view(request):
    """
    ネットワーク表示画面の枠組みを返す
    """
    return render(request, 'Core/graph.html')


@login_required
def graph_api(request):
    """p5.jsに読み込ませるためのノードとエッジのJSONデータを返す"""
    events = Event.objects.all()

    nodes_dict = {}
    links = []

    for event in events:
        # 1. ユーザーノード（人）
        user_node_id = f"user_{event.user.id}" if event.user else "user_unknown"
        user_name = event.user.username if event.user else "Unknown"
        if user_node_id not in nodes_dict:
            nodes_dict[user_node_id] = {"id": user_node_id, "label": user_name, "group": "user"}

        # 2. タグノード（場所・モノ）
        tag_node_id = f"tag_{event.tag_id}"
        if tag_node_id not in nodes_dict:
            nodes_dict[tag_node_id] = {"id": tag_node_id, "label": event.tag_id, "group": "location"}

        # 3. イベントノード（思考内容）
        event_node_id = f"event_{event.id}"
        short_text = event.text[:10] + "..." if len(event.text) > 10 else event.text
        nodes_dict[event_node_id] = {"id": event_node_id, "label": short_text, "group": "thought"}

        # 4. エッジ（線）を結ぶ
        # 人 → 思考
        links.append({"source": user_node_id, "target": event_node_id})
        # 場所 → 思考
        links.append({"source": tag_node_id, "target": event_node_id})

    # リスト形式に変換してJSONで返す
    data = {
        "nodes": list(nodes_dict.values()),
        "links": links
    }
    return JsonResponse(data)


@login_required
def personal_graph_view(request):
    """
    個人のネットワーク表示画面
    """
    return render(request, 'Core/personal_graph.html')


@login_required
def personal_graph_api(request):
    """
    p5.jsに読み込ませるための個人用ネットワークデータ
    """
    current_user = request.user

    # 1. データベース上の「すべての場所(tag_id)」を重複なしで取得
    all_locations = Event.objects.values_list('tag_id', flat=True).distinct()

    # 2. 「現在のユーザー」の思考ログだけを取得
    user_events = Event.objects.filter(user=current_user)

    # ユーザーが訪れたことのある場所のリストを作成
    visited_locations = set(user_events.values_list('tag_id', flat=True))

    nodes_dict = {}
    links = []

    # --- ノードの作成 ---
    # ① すべての場所ノード（訪れた場所と未訪問でグループを分ける）
    for loc in all_locations:
        tag_node_id = f"tag_{loc}"
        if loc in visited_locations:
            group = "visited_location"
        else:
            group = "unvisited_location"

        nodes_dict[tag_node_id] = {"id": tag_node_id, "label": loc, "group": group}

    # ② 自分の思考ノードとエッジ（線）
    for event in user_events:
        event_node_id = f"event_{event.id}"
        short_text = event.text[:10] + "..." if len(event.text) > 10 else event.text
        nodes_dict[event_node_id] = {"id": event_node_id, "label": short_text, "group": "thought"}

        # 線を繋ぐ：場所 ── 思考 （※自分との繋がりは削除）
        tag_node_id = f"tag_{event.tag_id}"
        links.append({"source": tag_node_id, "target": event_node_id})

    data = {
        "nodes": list(nodes_dict.values()),
        "links": links
    }
    return JsonResponse(data)
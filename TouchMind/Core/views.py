from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
from . import services
from .models import Event, Location
from .services import get_personalized_suggestion


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


@login_required
def personal_event_list(request):
    """
    自分だけの思考ログ（履歴）画面
    """
    # filter(user=request.user) で自分のデータだけを抽出
    # ※ id の降順（新しい順）などで並び替える場合は .order_by('-id') 等を付ける
    events = Event.objects.filter(user=request.user).order_by('-id')
    return render(request, 'Core/personal_list.html', {'events': events})


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
    """
    p5.jsに読み込ませるためのノードとエッジのJSONデータを返す
    """
    events = Event.objects.all()

    # DBからすべてのLocation情報を取得し、tag_idをキーにした辞書を作成
    locations_info = {loc.tag_id: loc for loc in Location.objects.all()}

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
            loc_obj = locations_info.get(event.tag_id)

            display_name = loc_obj.name if loc_obj else event.tag_id
            detail_text = loc_obj.description if loc_obj else "未登録の場所です。"
            category = loc_obj.category if loc_obj else "unknown"

            nodes_dict[tag_node_id] = {
                "id": tag_node_id,
                "label": display_name,
                "group": "location",
                "detail": detail_text,
                "category": category
            }

        # 3. イベントノード（思考内容）
        event_node_id = f"event_{event.id}"
        short_text = event.text[:10] + "..." if len(event.text) > 10 else event.text
        nodes_dict[event_node_id] = {"id": event_node_id, "label": short_text, "group": "thought"}

        # 4. エッジ（線）を結ぶ
        links.append({"source": user_node_id, "target": event_node_id})
        links.append({"source": tag_node_id, "target": event_node_id})

    # ★追加：Eventには存在しないが、Locationとして事前登録されている場所もノードとして追加する
    for loc in Location.objects.all():
        tag_node_id = f"tag_{loc.tag_id}"
        if tag_node_id not in nodes_dict:
            nodes_dict[tag_node_id] = {
                "id": tag_node_id,
                "label": loc.name if loc.name else loc.tag_id,
                "group": "unvisited_location", # ここはパーソナルグラフと色を合わせるか、locationのままでもOKです
                "detail": loc.description if loc.description else "未登録の場所です。",
                "category": loc.category
            }

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

    # ★変更：EventテーブルとLocationテーブルの両方からタグを取得し、重複をなくす
    event_locations = set(Event.objects.values_list('tag_id', flat = True))
    registered_locations = set(Location.objects.values_list('tag_id', flat = True))
    all_locations = event_locations.union(registered_locations)

    # 2. 「現在のユーザー」の思考ログだけを取得
    user_events = Event.objects.filter(user=current_user)

    # ユーザーが訪れたことのある場所のリストを作成
    visited_locations = set(user_events.values_list('tag_id', flat = True))

    # DBからすべてのLocation情報を取得し、tag_idをキーにした辞書を作成
    locations_info = {loc.tag_id: loc for loc in Location.objects.all()}

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

        # Locationテーブルに情報があればそれを使用し、なければIDをそのまま使う
        loc_obj = locations_info.get(loc)
        display_name = loc_obj.name if loc_obj else loc
        detail_text = loc_obj.description if loc_obj else "未登録の場所です。"
        category = loc_obj.category if loc_obj else "unknown"

        nodes_dict[tag_node_id] = {
            "id": tag_node_id,
            "label": display_name,
            "group": group,
            "detail": detail_text,
            "category": category
        }

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


@login_required
def personalized_suggestion_api(request):
    """
    現在のtag_idとユーザー情報から、最適な提案を返すAPI
    """
    tag_id = request.GET.get('tag_id', '')

    if not tag_id:
        return JsonResponse({"status": "error", "message": "tag_id is required"}, status = 400)

    # 提案ロジックを呼び出し
    suggestion = get_personalized_suggestion(request.user, tag_id)

    return JsonResponse(suggestion)


@login_required
def location_manager_view(request):
    """
    場所管理画面の表示
    """
    return render(request, 'Core/location_manager.html')


@login_required
def get_locations_api(request):
    """
    登録済みの場所一覧を返すAPI
    """
    locations = Location.objects.all().order_by('-id')
    data = [{
        "id": loc.id,
        "tag_id": loc.tag_id,
        "name": loc.name,
        "category": loc.category,
        "description": loc.description or ""
    } for loc in locations]
    return JsonResponse({"status": "success", "locations": data})


@login_required
@require_POST
def bulk_add_locations_api(request):
    """
    複数の場所をまとめて追加するAPI
    """
    try:
        data = json.loads(request.body)
        locations_data = data.get('locations', [])

        created_count = 0
        for item in locations_data:
            tag_id = item.get('tag_id', '').strip()
            if not tag_id:
                continue

            # すでに存在する tag_id の場合はスキップ、または上書き（今回は安全のため作成のみ）
            if Location.objects.filter(tag_id = tag_id).exists():
                continue

            # Locationの作成 (nameが空ならモデルのsave()で自動補完されます)
            Location.objects.create(
                tag_id = tag_id,
                name = item.get('name', '').strip(),
                category = item.get('category', 'work'),
                description = item.get('description', '').strip()
            )
            created_count += 1

        return JsonResponse({"status": "success", "message": f"{created_count}件の場所を追加しました。"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status = 400)


@login_required
@require_POST
def update_location_api(request):
    """
    既存の場所の詳細を後から変更するAPI
    """
    try:
        data = json.loads(request.body)
        tag_id = data.get('tag_id', '')

        location = Location.objects.filter(tag_id = tag_id).first()
        if not location:
            return JsonResponse({"status": "error", "message": "指定された場所が見つかりません。"}, status = 404)

        # 情報を更新
        location.name = data.get('name', '').strip() or tag_id # 空ならtag_idにする
        location.category = data.get('category', 'work')
        location.description = data.get('description', '').strip()
        location.save()

        return JsonResponse({"status": "success", "message": "場所の情報を更新しました。"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status = 400)


@login_required
@require_POST
def delete_location_api(request):
    """指定された場所（および任意で関連する思考ログ）を削除するAPI"""
    try:
        data = json.loads(request.body)
        tag_id = data.get('tag_id', '')

        # フロントエンドから「思考ログも消すか」の選択を受け取る
        delete_events = data.get('delete_events', False)

        location = Location.objects.filter(tag_id=tag_id).first()
        if not location:
            return JsonResponse({"status": "error", "message": "指定された場所が見つかりません。"}, status = 404)

        # 1. まず場所の登録データを削除
        location.delete()
        message = f"「{tag_id}」の場所設定を削除しました。"

        # 2. ユーザーが「思考ログも消す」を選択した場合
        if delete_events:
            # 現在のユーザーがその場所で記録したEvent（思考）をすべて削除
            deleted_count, _ = Event.objects.filter(user=request.user, tag_id=tag_id).delete()
            message = f"「{tag_id}」と、そこでの思考ログ（{deleted_count}件）をネットワークから完全に削除しました。"

        return JsonResponse({"status": "success", "message": message})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status = 400)
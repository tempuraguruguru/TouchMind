import datetime
from sentence_transformers import SentenceTransformer
from .models import Event, Location

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_time_phase(dt: datetime.datetime) -> str:
    """
    時間から文脈（morning・afternoon・nightなど）を抽出する
    """
    hour = dt.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour <18:
        return "afternoon"
    elif 18 <= hour < 24:
        return "night"
    else:
        return "midnight"


def process_nfc_event(tag_id: str, text: str, user = None, emotion_tag: str = ""):
    """
    イベント生成の一連の流れを管理
    タグID、入力テキスト、時間の文脈（morning・afternoon・nightなど）、心情、入力テキストと時間の文脈の埋め込みベクトル
    """
    now = datetime.datetime.now()
    time_phase = get_time_phase(now) ## 今の時間から文脈を抽出

    ## 時間などの文脈も加味してベクトル化
    contextual_text = f"[{time_phase}] {text}"
    embedding = model.encode(contextual_text).tolist()

    event = Event.objects.create(
        user = user,
        tag_id = tag_id,
        text = text,
        time_phase = time_phase,
        # emotion_tag = emotion_tag,
        embedding = embedding
    )
    return event


def get_personalized_suggestion(user, current_tag_id):
    """
    ユーザーの過去の背景情報とその場所のコンテキストから、
    最適なインサイト（提案）を抽出するロジック
    """
    # 1. 現在タッチした場所の情報を取得
    location = Location.objects.filter(tag_id = current_tag_id).first()
    location_name = location.name if location else current_tag_id

    # 2. ユーザーの「この場所での過去の記録」を古い順に取得
    past_events_at_loc = Event.objects.filter(user = user, tag_id = current_tag_id).order_by('id')

    # 3. ユーザーの「すべての場所での直近の記録（最新3件）」を取得して現在の関心を分析
    recent_events = Event.objects.filter(user = user).order_by('-id')[:3]

    if not past_events_at_loc.exists():
        # 初めて訪れた場所、またはまだ記録がない場合
        return {
            "type": "welcome",
            "title": f"📍 新しい空間: {location_name}",
            "message": f"この場所でのあなたの思考ログはまだありません。新鮮な気持ちで、今頭に浮かんでいることを残してみましょう！"
        }

    # 4. 【簡易的な背景解析ロジック】
    # 直近の関心事（最新の投稿テキスト）に含まれるキーワードが、過去にこの場所で考えたことにあるか探す
    recent_text = "".join([e.text for e in recent_events])

    # 過去のログから、今の関心に少しでもかすりそうなものを1件抽出
    best_match_event = None
    for past_event in reversed(past_events_at_loc): # 新しい過去ログから順にスキャン
        # 簡易的な単語マッチ（後にベクトル類似度に置き換えるコア部分）
        # 共通の文字が3文字以上あれば関連ありとみなす
        common_chars = set(past_event.text) & set(recent_text)
        if len(common_chars) >= 3:
            best_match_event = past_event
            break

    # マッチするものがなければ、この場所で一番昔に考えていたこと（原点）を出す
    if not best_match_event:
        best_match_event = past_events_at_loc.first()
        suggestion_type = "recall_origin"
        title = f"⏳ この場所での原点回帰"
    else:
        suggestion_type = "semantic_reconnect"
        title = f"💡 過去の思考とのシンクロ"

    return {
        "type": suggestion_type,
        "title": title,
        "message": f"以前ここで「{best_match_event.text}」と考えていました。このテーマについて、さらに深掘りしてみませんか？"
    }
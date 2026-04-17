import datetime
from sentence_transformers import SentenceTransformer
from .models import Event

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


def process_nfc_event(tag_id: str, text: str, emotion_tag: str = ""):
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
        tag_id = tag_id,
        text = text,
        time_phase = time_phase,
        # emotion_tag = emotion_tag,
        embedding = embedding
    )
    return event
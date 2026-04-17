from django.db import models
from pgvector.django import VectorField

class Event(models.Model):
    """
    システムの中核となるデータ構造
    「時間」と「ベクトル」を保存できる
    """
    ## 現実のトリガー
    ### id = models.BigAutoField(primary_key=True) ← Djangoはこの主キーを自動追加してくれる
    tag_id = models.CharField(max_length = 100, help_text = "NFCタグの固有ID")

    ## 時間と文脈
    timestamp = models.DateTimeField(auto_now_add = True)
    time_phase = models.CharField(max_length = 50, help_text = "morning, afternoon, nightなど")

    ## ユーザー入力
    text = models.TextField(help_text = "思考や出来事")
    emotion_tag = models.CharField(max_length = 50, blank = True, null = True, help_text = "任意の手動タグ")

    ## 構造化データ（ベクトル）
    embedding = VectorField(dimensions = 384, null = True, blank = True)

    def __str__(self):
        return f"{self.tag_id} at {self.time_phase} - {self.text[:20]}"
from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField

class Location(models.Model):
    """
    NFCタグ（場所）のコンテキストを保持するモデル
    """

    CATEGORY_CHOICES = [
        ('work', '💻 ワーク（研究・作業）'),
        ('relax', '☕ リラックス（カフェ・自宅）'),
        ('transit', '🚃 移動・その他'),
    ]

    # NFCに書き込むID (例: 'lab_desk', 'kichijoji_cafe' など)
    tag_id = models.CharField(max_length = 100, unique = True, help_text = "NFCに書き込まれる一意のID")

    # 画面に表示するわかりやすい名前
    name = models.CharField(max_length = 100, blank = True, help_text = "表示名 (例: 赤石研デスク, 吉祥寺のカフェ)")

    # 場所のカテゴリ（これを使って色を変えたりできます）
    category = models.CharField(max_length = 20, choices = CATEGORY_CHOICES, default = 'work')

    # その場所が持つ「静的なコンテキスト」
    description = models.TextField(blank = True, null = True, help_text = "この場所のコンテキストやメモ")
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        保存処理をカスタマイズする
        """
        # もし name が空（未入力）だった場合、tag_id の値を代入する
        if not self.name:
            self.name = self.tag_id
        # 本来の保存処理を実行する
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.category} ({self.tag_id}): [{self.description}]\n"


class Event(models.Model):
    """
    システムの中核となるデータ構造
    「時間」と「ベクトル」を保存できる
    """
    ## 現実のトリガー
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)

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
        # 誰がどこで記録したか分かるように修正
        return f"{self.user.username if self.user else 'Unknown'} at {self.tag_id} - {self.timestamp}"
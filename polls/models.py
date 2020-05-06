import datetime

from django.db import models
from django.utils import timezone
"""
- 各モデル（テーブルに該当）は一つのクラスで表現され、
  いずれも django.db.models.Model のサブクラスとなる。
- 個々のクラス変数はモデル（テーブル）のデータベースフィールドを表現している。

<モデルを作ったあとのコマンド>
python manage.py makemigrations polls
  makemigrations を実行することで、Djangoにモデルに変更があったことを伝え、
  そして変更を マイグレーション の形で保存することができる。

python manage.py sqlmigrate polls 0001
  コマンドは実際にはデータベースにマイグレーションを実行しない。
  DjangoがどのようなSQLをデータベースに発行するかを確認するために使用する。

python manage.py migrate
  モデルのテーブルをデータベースに作成
"""


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    # Field の最初の位置引数には、オプションとして人間が読めるフィールド名も指定可能
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        """投稿されたのが1日以内か

        Returns:投稿されたのが1日以内、かつ過去日時ならTrue
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    # Django は外部キーのフィールド名に "_id" を追加
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

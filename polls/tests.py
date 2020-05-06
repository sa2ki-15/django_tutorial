import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

"""テスト実行時の動作について
    - manage.py test polls は、polls アプリケーション内にあるテストファイル(test～.py)を探します
    - django.test.TestCase クラスのサブクラスを発見します
    - テストのための特別なデータベースを作成します
    - テスト用のメソッドとして、test で始まるメソッドを探します
    - test_was_published_recently_with_future_question の中で、
      pub_date フィールドに今日から30日後の日付を持つ Question インスタンスが作成されます
    - そして最後に、 assertIs() メソッドを使うことで、本当に返してほしいのは False だったにもかかわらず、
      was_published_recently() が True を返していることを発見します
"""

"""テストコードを実装するときのコツ
    - モデルやビューごとに TestClass を分割する
    - テストしたい条件の集まりのそれぞれに対して、異なるテストメソッドを作る
    - テストメソッドの名前は、その機能を説明するようなものにする
"""

"""テストの実行方法
    1. tests.pyを実行
       python manage.py test polls
    2. カバレッジの取得(※coverage.pyを環境にインストールしていること(pip install coverage))
        coverage run --source='.' manage.py test polls
    3. カバレッジレポートの取得
        coverage report
        coverage html
"""

class QuestionModelTests(TestCase):
    """Question モデルのテストクラス"""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() は、公開日が未来の日付である場合、Falseを返却する。
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """IndexViewのテストクラス"""

    def test_no_questions(self):
        """
        もしQuestionが存在しなければ、適切なメッセージを表示する。
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        公開日が過去日であるQuestionはindexページに表示される。
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        公開日が未来日であるQuestionはindexページに表示されない。
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        公開日が過去日と未来日のQuestionが混在する場合、過去日のQuestionのみ表示される。
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        indexページには複数のQuestionが表示される。
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

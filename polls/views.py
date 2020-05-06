from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.utils import timezone

from .models import Choice, Question


"""
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list,
    }

    # template = loader.get_template('polls/index.html')
    # return HttpResponse(template.render(context, request))

    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")

    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

"""


class IndexView(generic.ListView):
    """一覧ページを対象とした汎用ビュー

    ListViewのメソッドをオーバーライドして出力を制御する。
    template_name 属性を指定すると、自動生成されたデフォルトのテンプレート名ではなく、
    指定したテンプレート名を使うように Django に伝えることができる。

    ListView では、自動的に生成されるコンテキスト変数は question_list になる。
    これを上書きするには、 context_object_name 属性を与え、 latest_question_list を代わりに使用すると指定する。
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """ListViewのget_querysetをオーバーライド

        このメソッドで定義されたクエリを発行してデータをcontext_object_nameに格納する。

        Returns: 直近公開された5件の質問(公開日が未来日のものは除く)
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """個別詳細ページを対象とした汎用ビュー

    レコード一列を対象としてデータを取得する。
    urls.pyの<int:pk>のpk(プライマリキー)を使用する。
    DetailViewはこの名前を使ってレコードを特定する。

    DetailView 汎用ビューには、 "pk" という名前で URL からプライマリキーをキャプチャして渡すことになっている。
    DetailView には question という変数が自動的に渡される。
    Django モデル (Question) を使用していて、 Django はコンテキスト変数にふさわしい名前を決めることができる。
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        公開日が未来日のものは除く
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    """投票

    同時に複数人が投票すると競合になる。以下が解決方法。
    https://docs.djangoproject.com/ja/3.0/ref/models/expressions/#avoiding-race-conditions-using-f
    F関数を使用することで、「UPDATE question SET votes = votes + 1 WHERE id = 1」のようなSQLが発行される。
    F関数を使用しないと、「UPDATE question SET votes = 2 WHERE id = 1」となって競合が起きる。

    HttpResponseRedirect : 引数のURLへのリダイレクトを行う。ユーザが戻るボタンで戻って二重投稿を防ぐ。
    reverse : URLへの逆変換を行う

    Args:
        request: HttpRequest
        question_id: 質問ID

    Returns: HttpResponseRedirect

    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):  # postにchoiceがない、または存在しないchoiceのとき例外
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

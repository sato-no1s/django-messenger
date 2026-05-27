from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.urls import reverse

from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.db.models import Prefetch
from django.db.models import OuterRef, Subquery
from django.db.models import Count

from .models import Group
from .models import GroupUser
from .models import Message

from .forms import GroupForm
from .forms import MessageForm

from lib.ai_engine import ask_ai
from django.db import connection
from django.utils import timezone


# Create your views here.
class IndexView(TemplateView):
    template_name = 'messenger/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'メッセンジャーくん'
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'messenger/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'メッセンジャーくん'
        
        # ログインユーザのIDを取得
        user_id = self.request.user.id
        
        # グループ一覧とログインユーザが参加しているかの情報を結合するSQL
        # 以下の2行でサブクエリを実行
        # サブクエリの作成
        query_gu = GroupUser.objects.filter(user=user_id, group=OuterRef('pk'))
        query_all = GroupUser.objects.filter(group=OuterRef('pk')).values('group').annotate(c=Count('*')).values('c')
        # メインクエリの作成
        object_list = Group.objects.annotate(
            attend_count=Count(Subquery(query_gu.values('user')[:1])),
            count=Subquery(query_all)
        )
        # グループ一覧とログインユーザの参加可否の結果を結合したQuerySet
        context['object_list'] = object_list
        return context

class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'messenger/group/list.html'
    paginate_by = 3
    
    def get_queryset(self):
        object_list = Group.objects.all().order_by('id')
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'グループ一覧'
        return context

class GroupCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('messenger:group_list')
    template_name = 'messenger/group/create.html'
    success_message = 'グループ新規登録が完了しました'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'グループ新規登録'
        return context

class GroupUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy('messenger:group_list')
    template_name = 'messenger/group/update.html'
    success_message = 'グループ更新が完了しました'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'グループ更新'
        return context

class GroupUserCreateView(LoginRequiredMixin, TemplateView):
    def get_success_url(self):
        # 新規登録処理完了後のリダイレクト先の設定
        return resolve_url('messenger:dashboard')
    
    def get(self, *args, **kwargs):
        # パス変数から参加対象のグループIDの取得
        group_id = self.kwargs.get('group_id')
        # ログインユーザのID取得
        user_id = self.request.user.id
        
        # 参加対象のグループにログインユーザが参加しているかどうかのチェック
        is_attended = GroupUser.objects.filter(group=group_id, user=user_id).exists()
        # 参加済みの判定
        if is_attended :
            # すでに参加しているので、登録処理は行わない
            messages.success(self.request, 'グループにすでに参加済みです')
            # グループ一覧に戻る
            return redirect(self.get_success_url())
        
        # 参加していないのでグループユーザーに新規登録処理
        group_user = GroupUser()
        # パス変数で指定したグループID
        group_user.group_id = group_id
        # ログインユーザのID
        group_user.user_id = user_id
        # データベースに新規登録
        group_user.save()
        # フラッシュメッセージの設定
        messages.success(self.request, 'グループに参加しました')
        # ダッシュボードにリダイレクト
        return redirect(self.get_success_url())

class MessageTalkView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message/talk.html'
    success_message = '新規メッセージを投稿しました'
    
    def get_success_url(self):
        # パス変数からグループIDの取得
        group_id = self.kwargs.get('group_id')
        # 登録処理終了後、現在のビューに移動する
        return reverse('messenger:message_talk', kwargs={'group_id': group_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'メッセージ一覧＆新規投稿'
        
        # パス変数からグループIDを取得
        group_id = self.kwargs.get('group_id')
        
        # パス変数で指定されたグループのメッセージ一覧を取得
        object_list = Message.objects.filter(group=group_id).select_related('user').order_by('created_at')
        context['object_list'] = object_list
        
        # パス変数で指定されたグループのモデルを取得
        object = Group.objects.filter(pk=group_id).first()
        context['object'] = object
        
        # 現在のビュー自身をテンプレートに渡す
        context['view'] = self
        return context
    
    def form_valid(self, form):
        # パス変数からグループIDを取得
        group_id = self.kwargs.get('group_id')
        # ログインユーザ情報を取得
        user_id = self.request.user.id
        
        # データベース保存前のモデルインスタンスを取得
        message = form.save(commit=False)
        # グループIDを代入
        message.group_id = group_id
        # ユーザIDを代入
        message.user_id = user_id
        # メッセージの実際の登録処理実行
        message.save()
        
        # フラッシュメッセージを設定
        messages.success(self.request, self.success_message)
        # 現在のビューにリダイレクト
        return redirect(self.get_success_url())

class MessageAITalkView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message/talk.html'
    success_message = '新規メッセージを投稿しました'
    
    def get_success_url(self):
        # パス変数からグループIDの取得
        group_id = self.kwargs.get('group_id')
        # 登録処理終了後、現在のビューに移動する
        return reverse('messenger:message_ai_talk', kwargs={'group_id': group_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'メッセージ一覧＆新規投稿'
        
        # パス変数からグループIDを取得
        group_id = self.kwargs.get('group_id')
        
        # パス変数で指定されたグループのメッセージ一覧を取得
        object_list = Message.objects.filter(group=group_id).select_related('user').order_by('created_at')
        context['object_list'] = object_list
        
        # パス変数で指定されたグループのモデルを取得
        object = Group.objects.filter(pk=group_id).first()
        context['object'] = object
        
        # 現在のビュー自身をテンプレートに渡す
        context['view'] = self
        # 現在のビュー自身をテンプレートに渡す
        context['is_ai'] = True

        return context
    
    def form_valid(self, form):
        # パス変数からグループIDを取得
        group_id = self.kwargs.get('group_id')
        # ログインユーザ情報を取得
        user_id = self.request.user.id
        
        # データベース保存前のモデルインスタンスを取得
        message = form.save(commit=False)
        # グループIDを代入
        message.group_id = group_id
        # ユーザIDを代入
        message.user_id = user_id
        # メッセージの実際の登録処理実行
        message.save()

        user_text = message.body
        ai_response_text = ask_ai(user_text)
        now = timezone.now()
        # Message.objects.create(
        #     group_id=group_id,
        #     user_id=0, # AIのIDとして0を指定
        #     body=ai_response_text
        # )        
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messenger_message (body, group_id, user_id, created_at, modified_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                [ai_response_text, group_id, 0, now, now] # user_idに0を指定
            )

        # フラッシュメッセージを設定
        messages.success(self.request, self.success_message)
        # 現在のビューにリダイレクト
        return redirect(self.get_success_url())
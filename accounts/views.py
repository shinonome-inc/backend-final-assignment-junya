from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView
from tweets.models import Tweet

from .forms import SignupForm
from .models import FriendShip

User = get_user_model()


class UserSignUpView(CreateView):
    model = User
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return response


class UserLoginView(LoginView):
    template_name = "accounts/login.html"


class UserLogoutView(LoginRequiredMixin, LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = "accounts/user_profile.html"
    model = Tweet
    context_object_name = "tweets"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Tweet.objects.select_related("user").filter(user=user)

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        context = super().get_context_data(**kwargs)
        context["user"] = user
        context["is_following"] = FriendShip.objects.filter(follower=self.request.user, following=user)
        context["following_count"] = FriendShip.objects.filter(follower=user).count()
        context["follower_count"] = FriendShip.objects.filter(following=user).count()

        return context


class FollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身をフォローすることはできません。")
            return HttpResponseBadRequest("you cannnot follow yourself.")
        if self.request.user.following.filter(following__username=target_user.username).exists():
            messages.add_message(request, messages.INFO, "既にフォローしています。")
        else:
            FriendShip.objects.create(follower=request.user, following=target_user)
            messages.add_message(request, messages.SUCCESS, "フォローしました。")
        return super().post(request, *args, **kwargs)


class UnFollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身にその操作をすることはできません。")
            return HttpResponseBadRequest("you cannnot unfollow yourself.")
        if FriendShip.objects.filter(following=target_user).filter(follower=self.request.user).exists():
            target_friend_obj = get_object_or_404(FriendShip, following=target_user, follower=self.request.user)
            target_friend_obj.delete()
            messages.add_message(request, messages.SUCCESS, "フォロー解除しました。")
        else:
            messages.add_message(request, messages.INFO, "フォローすらしていません")
        return super().post(request, *args, **kwargs)


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/following_list.html"
    context_object_name = "following_list"

    def get_queryset(self):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        return target_user.follower.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(User, username=self.kwargs["username"])
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/follower_list.html"
    context_object_name = "follower_list"

    def get_queryset(self):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        return target_user.following.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(User, username=self.kwargs["username"])
        return context

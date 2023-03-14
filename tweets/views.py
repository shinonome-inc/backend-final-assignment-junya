from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet
    context_object_name = "tweets"
    queryset = model.objects.select_related("user").order_by("-created_at")


class MyPost(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"

    def get_queryset(self):
        return Tweet.objects.filter(user=self.request.user)


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/detail.html"
    model = Tweet


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    template_name = "tweets/create.html"
    fields = ["title", "content"]
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "tweets/delete.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        return self.request.user == self.get_object().user

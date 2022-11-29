from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignupForm

User = get_user_model()


class SignUpView(CreateView):
    model = User
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:home")


class HomeView(TemplateView):
    template_name = "accounts/home.html"


# Create your views here.

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm


class SignUpView(CreateView):
    model = get_user_model()
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("index")


# Create your views here.

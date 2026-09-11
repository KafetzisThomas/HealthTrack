from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.is_active = False
            account.save()
            messages.success(request, "Account pending approval.")
            return redirect("accounts:login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})

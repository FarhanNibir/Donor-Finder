from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProfileForm, RegistrationForm
from .models import DonorProfile

def register(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Your BloodLink account has been created successfully!'
            )

            return redirect('home:home')
    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


@login_required
def profile(request):
    donor, _ = DonorProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=donor)

    return render(request, "accounts/profile.html", {"form": form, "donor": donor})


@login_required
@require_POST
def mark_donated(request):
    donor = get_object_or_404(DonorProfile, user=request.user)
    donor.last_donated_at = timezone.localdate()
    donor.save(update_fields=["last_donated_at"])
    messages.success(
        request,
        "Thank you for donating! You'll be hidden from search for the next 4 months.",
    )
    return redirect("accounts:profile")
from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from accounts.models import BLOOD_GROUPS, COOLDOWN_DAYS, DonorProfile

# patient's blood group -> donor groups that can give to them
COMPATIBLE_DONORS = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}

MAX_RESULTS = 50


def home(request):
    blood_cards = [
        (value, value.replace("+", " Positive").replace("-", " Negative"))
        for value, _ in BLOOD_GROUPS
    ]

    blood_group = request.GET.get("blood_group", "").strip()
    if blood_group not in COMPATIBLE_DONORS:
        blood_group = ""
    district = request.GET.get("district", "").strip()
    area = request.GET.get("area", "").strip()
    exact = request.GET.get("exact") == "1"
    searched = bool(request.GET)

    context = {
        "blood_cards": blood_cards,
        "districts": (
            DonorProfile.objects.exclude(district="")
            .order_by("district")
            .values_list("district", flat=True)
            .distinct()
        ),
        "blood_group": blood_group,
        "district": district,
        "area": area,
        "exact": exact,
        "searched": searched,
    }

    if searched:
        # available = never donated, or last donation was 4+ months ago
        cutoff = timezone.localdate() - timedelta(days=COOLDOWN_DAYS)
        donors = (
            DonorProfile.objects.select_related("user")
            .filter(is_active=True)
            .exclude(blood_group="")
            .filter(Q(last_donated_at__isnull=True) | Q(last_donated_at__lte=cutoff))
        )
        if request.user.is_authenticated:
            donors = donors.exclude(user=request.user)
        if blood_group:
            groups = [blood_group] if exact else COMPATIBLE_DONORS[blood_group]
            donors = donors.filter(blood_group__in=groups)
        if district:
            donors = donors.filter(district__icontains=district)
        if area:
            donors = donors.filter(area__icontains=area)

        donors = donors.order_by("district", "area", "blood_group")
        context["total"] = donors.count()
        context["donors"] = donors[:MAX_RESULTS]
        context["max_results"] = MAX_RESULTS

    return render(request, "home/home.html", context)
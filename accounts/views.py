import random
import re

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ForgotPasswordForm, LoginForm, OTPForm, ProfileEditForm, ResetPasswordForm, SignupForm
from .models import CandidateProfile, JobApplication


def home_view(request):
    if not request.user.is_authenticated:
        return redirect("register")
    profile = getattr(request.user, "candidateprofile", None)
    return render(request, "index.html", {"profile": profile})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignupForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            User = get_user_model()
            user = User.objects.create_user(
                username=form.cleaned_data["email"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                is_active=False,
            )
            profile = CandidateProfile.objects.create(
                user=user,
                phone=form.cleaned_data["phone"],
                user_type=form.cleaned_data["user_type"],
                profile_photo=form.cleaned_data.get("profile_photo"),
                disability=form.cleaned_data["disability"],
                current_location=form.cleaned_data["current_location"],
                preferred_location=form.cleaned_data["preferred_location"],
                education=form.cleaned_data["education"],
                employment_history=form.cleaned_data["employment_history"],
                skills=form.cleaned_data["skills"],
                resume=form.cleaned_data.get("resume"),
                hide_from_recruiters=form.cleaned_data["hide_from_recruiters"],
                communication_settings="job_alerts=on" if form.cleaned_data["job_alerts"] else "job_alerts=off",
            )
            if profile.resume:
                profile.resume_keywords = extract_keywords(profile.resume.name, profile.skills)
                profile.save()
        issue_otp(request, user, "signup")
        messages.success(request, "Account created. Verify the OTP sent to your email/mobile to activate it.")
        return redirect("verify_otp")
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]
        if not user.is_active:
            issue_otp(request, user, "login_verify")
            messages.info(request, "Please verify OTP before we open your account.")
            return redirect("verify_otp")
        profile = getattr(user, "candidateprofile", None)
        needs_otp = profile and not (profile.email_verified and profile.phone_verified)
        if needs_otp:
            issue_otp(request, user, "login_verify")
            messages.info(request, "A quick OTP check is needed before login.")
            return redirect("verify_otp")
        login(request, user)
        if not form.cleaned_data["remember"]:
            request.session.set_expiry(0)
        if profile:
            profile.mark_active()
        messages.success(request, "Welcome back. Your dashboard is ready.")
        return redirect("home")
    return render(request, "login.html", {"form": form})


def verify_otp_view(request):
    pending_user_id = request.session.get("otp_user_id")
    if not pending_user_id:
        messages.error(request, "OTP session expired. Please try again.")
        return redirect("login")
    user = get_user_model().objects.filter(id=pending_user_id).first()
    if not user:
        messages.error(request, "Account not found. Please register again.")
        return redirect("register")

    form = OTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["otp"] != request.session.get("otp_code"):
            form.add_error("otp", "Incorrect OTP.")
        else:
            profile = getattr(user, "candidateprofile", None)
            user.is_active = True
            user.save(update_fields=["is_active"])
            if profile:
                profile.email_verified = True
                profile.phone_verified = True
                profile.last_active_at = timezone.now()
                profile.freshness_score = 100
                profile.save(
                    update_fields=[
                        "email_verified",
                        "phone_verified",
                        "last_active_at",
                        "freshness_score",
                        "profile_completion",
                        "updated_at",
                    ]
                )
            flow = request.session.get("otp_flow")
            clear_otp(request)
            if flow == "reset_password":
                request.session["reset_user_id"] = user.id
                return redirect("reset_password")
            login(request, user)
            messages.success(request, "Verification complete. Your profile is now searchable.")
            return redirect("home")
    return render(request, "verify_otp.html", {"form": form, "otp_hint": request.session.get("otp_code")})


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = get_user_model().objects.get(email__iexact=form.cleaned_data["email"])
        issue_otp(request, user, "reset_password")
        messages.info(request, "OTP sent. Verify it to reset your password.")
        return redirect("verify_otp")
    return render(request, "forgot_password.html", {"form": form})


def reset_password_view(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        messages.error(request, "Password reset session expired.")
        return redirect("forgot_password")
    user = get_user_model().objects.filter(id=user_id).first()
    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid() and user:
        user.set_password(form.cleaned_data["password"])
        user.save(update_fields=["password"])
        request.session.pop("reset_user_id", None)
        messages.success(request, "Password changed. Please login.")
        return redirect("login")
    return render(request, "reset_password.html", {"form": form})


@login_required
def profile_view(request):
    profile, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={"phone": f"pending-{request.user.id}"},
    )
    initial = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "phone": profile.phone,
        "user_type": profile.user_type,
        "disability": profile.disability,
        "current_location": profile.current_location,
        "preferred_location": profile.preferred_location,
        "education": profile.education,
        "employment_history": profile.employment_history,
        "skills": profile.skills,
        "hide_from_recruiters": profile.hide_from_recruiters,
        "job_alerts": "job_alerts=on" in profile.communication_settings,
    }
    edit_form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
        profile=profile,
        initial=initial,
    )
    if request.method == "POST" and edit_form.is_valid():
        request.user.first_name = edit_form.cleaned_data["first_name"]
        request.user.last_name = edit_form.cleaned_data["last_name"]
        request.user.email = edit_form.cleaned_data["email"]
        request.user.username = edit_form.cleaned_data["email"]
        request.user.save(update_fields=["first_name", "last_name", "email", "username"])

        profile.phone = edit_form.cleaned_data["phone"]
        profile.user_type = edit_form.cleaned_data["user_type"]
        profile.disability = edit_form.cleaned_data["disability"]
        profile.current_location = edit_form.cleaned_data["current_location"]
        profile.preferred_location = edit_form.cleaned_data["preferred_location"]
        profile.education = edit_form.cleaned_data["education"]
        profile.employment_history = edit_form.cleaned_data["employment_history"]
        profile.skills = edit_form.cleaned_data["skills"]
        profile.hide_from_recruiters = edit_form.cleaned_data["hide_from_recruiters"]
        profile.communication_settings = "job_alerts=on" if edit_form.cleaned_data["job_alerts"] else "job_alerts=off"
        if edit_form.cleaned_data.get("profile_photo"):
            profile.profile_photo = edit_form.cleaned_data["profile_photo"]
        if edit_form.cleaned_data.get("resume"):
            profile.resume = edit_form.cleaned_data["resume"]
            profile.resume_keywords = extract_keywords(profile.resume.name, profile.skills)
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    applications = JobApplication.objects.filter(user=request.user)
    recommended_jobs = recommend_jobs(profile)
    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "applications": applications,
            "recommended_jobs": recommended_jobs,
            "edit_form": edit_form,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


@login_required
@require_POST
def update_resume_view(request):
    profile, _ = CandidateProfile.objects.get_or_create(
        user=request.user,
        defaults={"phone": f"pending-{request.user.id}"},
    )
    resume = request.FILES.get("resume")
    if not resume:
        messages.error(request, "Please choose a resume file first.")
        return redirect("home")
    profile.resume = resume
    profile.resume_keywords = extract_keywords(resume.name, profile.skills)
    profile.save()
    messages.success(request, "Resume updated successfully.")
    return redirect("home")


@require_POST
def apply_job_view(request):
    job_title = request.POST.get("job_title", "Selected Job").strip()
    if not request.user.is_authenticated:
        request.session["pending_job_application"] = job_title
        messages.info(request, "Create an account or login before applying.")
        return redirect(f"{reverse('register')}?next=apply")
    JobApplication.objects.get_or_create(user=request.user, job_title=job_title)
    messages.success(request, f"Application submitted for {job_title}.")
    return redirect("profile")


def issue_otp(request, user, flow):
    code = f"{random.randint(100000, 999999)}"
    request.session["otp_user_id"] = user.id
    request.session["otp_code"] = code
    request.session["otp_flow"] = flow
    send_mail(
        "AbilityJobs verification OTP",
        f"Your AbilityJobs OTP is {code}.",
        "support@abilityjobs.com",
        [user.email],
        fail_silently=True,
    )


def clear_otp(request):
    for key in ["otp_user_id", "otp_code", "otp_flow"]:
        request.session.pop(key, None)


def extract_keywords(filename, skills):
    words = re.findall(r"[A-Za-z][A-Za-z+#.]{2,}", f"{filename} {skills}")
    stop = {"resume", "doc", "docx", "pdf"}
    return ", ".join(sorted({word.lower() for word in words if word.lower() not in stop})[:20])


def recommend_jobs(profile):
    skills = profile.skills.lower()
    jobs = [
        ("Data Entry Operator", "Remote", "Entry level", "Excel, typing, back-office"),
        ("Customer Support Executive", "Remote", "Fresher friendly", "Communication, email, chat"),
        ("Graphic Designer", "Hybrid", "Portfolio preferred", "Design, Canva, Photoshop"),
        ("Accessibility Tester", "Remote", "Growing role", "Testing, WCAG, attention to detail"),
        ("Website Assistant", "Hybrid", "Flexible hours", "Website updates, email support"),
        ("Content Coordinator", "Remote", "NGO partner", "Proofreading, documents, training content"),
        ("Office Operations Executive", "On-site", "Accessible workplace", "Scheduling, records, coordination"),
    ]
    if "design" in skills or "photoshop" in skills:
        jobs.insert(0, jobs.pop(2))
    return jobs[:3]

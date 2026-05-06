from django.urls import path

from . import views

urlpatterns = [
    path("register.html", views.signup_view, name="register"),
    path("login.html", views.login_view, name="login"),
    path("verify-otp.html", views.verify_otp_view, name="verify_otp"),
    path("forgot-password.html", views.forgot_password_view, name="forgot_password"),
    path("reset-password.html", views.reset_password_view, name="reset_password"),
    path("profile.html", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
    path("update-resume/", views.update_resume_view, name="update_resume"),
    path("apply/", views.apply_job_view, name="apply_job"),
]

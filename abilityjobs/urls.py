from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.static import serve
from accounts.views import home_view


HTML_PAGES = {
    "index.html",
    "jobs.html",
    "job.html",
    "employer-dashboard.html",
    "ngos.html",
}


def page_view(request, page_name):
    if page_name == "index.html":
        return redirect("/")
    if page_name == "job.html":
        return redirect("/jobs.html")
    if page_name not in HTML_PAGES:
        raise Http404("Page not found")
    return TemplateView.as_view(template_name=page_name)(request)


urlpatterns = [
    path("", ensure_csrf_cookie(home_view), name="home"),
    path("", include("accounts.urls")),
    re_path(
        r"^(?P<path>images/.*|app\.js)$",
        serve,
        {"document_root": settings.BASE_DIR},
        name="static-root-asset",
    ),
    path("<str:page_name>", ensure_csrf_cookie(page_view), name="page"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

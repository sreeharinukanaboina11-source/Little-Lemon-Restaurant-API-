from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from restaurant.views import home_view

urlpatterns = [
    # Static HTML homepage (Coursera requirement: Django serves static HTML content)
    path("", home_view, name="home"),
    path("restaurant/", home_view, name="restaurant_home"),

    # Django Administration
    path("admin/", admin.site.urls),

    # REST APIs
    path("api/", include("restaurant.urls")),
    path("restaurant/api/", include("restaurant.urls")),

    # Token Authentication endpoints
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("api/token/login/", obtain_auth_token, name="api_token_login"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

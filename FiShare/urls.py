from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from users import views as users_view
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', users_view.register, name='register'),
    path('profile/', users_view.profile, name='profile'),
    path('', include('allusers.urls')),
    path('', include('root.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

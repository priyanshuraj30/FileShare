from django.urls import path,include
from users import views as users_view
from django.conf.urls.static import static
from django.conf import settings
from root.views import MyFileFolderView


urlpatterns = [
    path('all_users/', users_view.user_list, name='all_users'),
    path('all_users/<int:user_id>', MyFileFolderView.as_view(template_name='root/home_base.html'),name='user_repo'),
    path('all_users/', include('root.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.new_post, name='new_post'),

    # страница с постами автора, на которого пользователь подписан
    path('follow/', views.follow_index, name='follow_index'),

    # подписаться
    path('<username>/follow', views.profile_follow, name='profile_follow'),
    # отписаться
    path('<username>/unfollow', views.profile_unfollow, name='profile_unfollow'),

    # профайл пользователя
    path('<username>/', views.profile, name='profile'),

    # просмотр записи
    path('<username>/<int:post_id>/', views.post_view, name='post'),

    # редактирование записи
    path('<username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),

    # комментарии
    path('<username>/<int:post_id>/comment', views.add_comment, name='add_comment'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

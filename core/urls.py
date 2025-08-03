from django.urls import path
from core.views.user import register, login, user_list, user_detail, user_update, user_delete
from core.views.subsystem_status import SubsystemStatusCRUD


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/', user_list, name='user-list'),
    path('users/<int:user_id>/', user_detail, name='user-detail'),
    path('users/<int:user_id>/update/', user_update, name='user-update'),
    path('users/<int:user_id>/delete/', user_delete, name='user-delete'),
    path('subsystem_status/', SubsystemStatusCRUD.as_view(), name='subsystem-status-crud'),
]
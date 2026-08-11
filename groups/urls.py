from django.urls import path

from . import views

urlpatterns = [
    path("", views.group_list, name="group_list"),
    path("create/", views.group_create, name="group_create"),
    path("invitations/<int:invitation_id>/accept/", views.invitation_accept, name="invitation_accept"),
    path("invitations/<int:invitation_id>/decline/", views.invitation_decline, name="invitation_decline"),
    path("<int:group_id>/", views.group_detail, name="group_detail"),
    path("<int:group_id>/edit/", views.group_edit, name="group_edit"),
    path("<int:group_id>/delete/", views.group_delete, name="group_delete"),
    path("<int:group_id>/members/", views.group_members, name="group_members"),
    path("<int:group_id>/members/invite/", views.group_invite, name="group_invite"),
    path(
        "<int:group_id>/members/<int:membership_id>/remove/",
        views.group_remove_member,
        name="group_remove_member",
    ),
    path("<int:group_id>/leave/", views.group_leave, name="group_leave"),
]

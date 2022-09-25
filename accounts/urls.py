from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy


urlpatterns = [
    # path("home/", views.home, name="accounts-home"),
    path(
        "",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/change_password.html",
            success_url=reverse_lazy("change_password"),
        ),
        name="change_password",
    ),
    path("register/", views.UserRegister.as_view(), name="register"),
    path("users/", views.UserList.as_view(), name="users"),
    path("createmv/", views.CreateVm.as_view(), name="createvm"),
    path("board/", views.ManageList.as_view(), name="board"),
    path("profile/", views.profile, name="profile"),
    path("gui_api/", views.user_api, name="gui_api"),
    path("spice_api/", views.spice_api, name="spice_api"),
    path("change_user/<slug:slug>/", views.VmDetail.as_view(), name="change_user"),
]

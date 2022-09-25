from django.views.generic.edit import FormView
from .forms import UserRegisterForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Vm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import VmForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from .api.new_openstack import (
    create_server,
    delete_server,
    checktoken,
    server_action,
    delete_server,
    get_flavors,
    get_images,
    get_spice,
)


# 注册
class UserRegister(SuccessMessageMixin, FormView):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")
    success_message = "注册成功，可以登陆！"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            form.save()
            return self.form_valid(form)

        else:
            return self.form_invalid(form)


class ManageList(LoginRequiredMixin, ListView):

    context_object_name = "vms"

    def get_template_names(self):
        if self.request.user.is_superuser:
            return "accounts/admin_board.html"
        else:
            return "accounts/board.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Vm.objects.all()
        else:
            # print(Vm.objects.filter(owner=self.request.user.username))
            return self.request.user.vm_set.all()

    def post(self, request, *args, **kwargs):
        server_ids = self.request.POST.getlist("ids")
        if self.request.user.is_superuser:

            if len(server_ids) != 0:
                scoped_token = checktoken()
                for server_id in server_ids:
                    if delete_server(scoped_token, server_id):
                        Vm.objects.get(vmid=server_id).delete()
            return redirect("board")
        else:
            if len(server_ids) != 0:
                scoped_token = checktoken()
                vms = self.request.user.vm_set.all()

                for vm in vms:
                    if vm.vmid in server_ids:
                        if vm.state == 0:
                            if server_action(scoped_token, vm.vmid, action="os-start"):
                                vm.state = 1
                                vm.save()
                    else:
                        if vm.state == 1:
                            if server_action(scoped_token, vm.vmid, action="os-stop"):
                                vm.state = 0
                                vm.save()

            else:

                vms = self.request.user.vm_set.all()
                if len(vms) > 0:
                    scoped_token = checktoken()
                    for vm in vms:
                        print(vm.vmid)
                        if server_action(scoped_token, vm.vmid, action="os-stop"):
                            vm.state = 0
                            vm.save()

            return redirect("board")


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, "您的个人信息已经变更成功!")
            return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {"u_form": u_form}

    return render(request, "accounts/profile.html", context)


class SuperTest(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class UserList(SuperTest, ListView):
    model = User
    context_object_name = "users"
    template_name = "accounts/admin_users.html"

    def post(self, request, *args, **kwargs):
        ids = self.request.POST.getlist("inputs")

        scoped_token = checktoken()
        for user_id in ids:
            user = User.objects.get(id=id)

            for vm in user.vm_set.all():
                server_id = vm.vmid
                delete_server(scoped_token, server_id)

        User.objects.filter(id__in=ids).delete()
        return redirect("users")


class CreateVm(SuperTest, SuccessMessageMixin, FormView):
    form_class = VmForm
    template_name = "accounts/createvm.html"
    success_url = reverse_lazy("createvm")
    success_message = "虚拟机创建成功！"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            vmname = self.request.POST.get("vmname")
            user_id = self.request.POST.get("user")
            flavor_id = self.request.POST.get("flavor")
            image_id = self.request.POST.get("image")
            if user_id:
                scoped_token = checktoken()
                server_id, password, ip = create_server(
                    scoped_token, vmname, image_id, flavor_id
                )
                if server_id:
                    user = User.objects.get(id=user_id)
                    Vm.objects.create(
                        vmname=vmname,
                        vmid=server_id,
                        ipaddr=ip,
                        password=password,
                        owner=user,
                        state=1,
                    )

                return self.form_valid(form)
            return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    # def get(self, request, *args, **kwargs):
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     context = self.get_context_data(**kwargs)
    #     context["form"] = form
    #     users = User.objects.all()
    #     context["users"] = users
    #     return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        context["users"] = users
        scoped_token = checktoken()
        images = get_images(scoped_token)
        context["images"] = images
        flavors = get_flavors(scoped_token)
        context["flavors"] = flavors
        return context


class VmDetail(SuperTest, SuccessMessageMixin, DetailView):
    model = Vm
    slug_field = "id"
    template_name = "accounts/vm_detail.html"
    success_message = "更换用户成功!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vm = Vm.objects.get(id=self.kwargs["slug"])
        users = User.objects.exclude(username=vm.owner)
        context["users"] = users

        return context

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get("user")
        vm = Vm.objects.get(id=self.kwargs["slug"])
        vm.owner = User.objects.get(id=user_id)
        vm.save()

        return redirect("board")


@csrf_exempt
@require_POST
def user_api(request):

    username = request.POST.get("u")
    password = request.POST.get("p")

    # print(username, password)
    user = User.objects.get(username=username)
    if user:
        if check_password(password, user.password):
            vms = user.vm_set.all()
            data = []
            for vm in vms:
                vm_data = {}
                vm_data["name"] = vm.vmname
                vm_data["ip"] = vm.ipaddr
                vm_data["password"] = vm.password
                vm_data["vmid"] = vm.vmid
                data.append(vm_data)

    return JsonResponse({"vms": data})


@csrf_exempt
@require_POST
def spice_api(request):

    vmid = request.POST.get("vmid")
    token = checktoken()
    vm = Vm.objects.get(vmid=vmid)
    if vm.state == 0:
        if server_action(token, vm.vmid, action="os-start"):
            vm.state = 1
            vm.save()
    # print(vmid)
    ip, port = get_spice(token, vmid)
    return JsonResponse({"data": {"ip": ip, "port": port}})

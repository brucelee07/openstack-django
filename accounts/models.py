from django.db import models

from django.contrib.auth.models import User


class Vm(models.Model):
    vmname = models.CharField(max_length=30, null=False)
    vmid = models.CharField(max_length=200, null=False)
    # image = models.CharField(max_length=100, null=True, blank=True)
    # flavor = models.CharField(max_length=100, null=True, blank=True)
    # network = models.CharField(max_length=100, null=True, blank=True)
    ipaddr = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=20, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    state = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_date",)

    def __str__(self):
        return f"vm: {self.vmid}, state: {self.state}"

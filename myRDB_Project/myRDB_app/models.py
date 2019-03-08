import datetime
import json

from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djongo import models as djongomodels
from django.utils import timezone

# Create your models here.
from rest_framework.authtoken.models import Token

from myRDB_Project import settings

class ChangeRequests(models.Model):
    requesting_user_pk = models.IntegerField()
    requesting_user = models.CharField(max_length=7)
    compare_user = models.CharField(max_length=7)
    action = models.CharField(max_length=10)
    right_name = models.CharField(max_length=150)
    right_type = models.CharField(max_length=5)
    reason_for_action = models.CharField(max_length=500)
    status = models.CharField(max_length=10, default="unanswered")
    reason_for_decline = models.CharField(max_length=500, default="")
    created = models.DateTimeField(auto_now_add=True, editable=False,null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False,null=False, blank=False)


# Create your models here.
class Orga(models.Model):
    team = models.CharField(max_length=100)
    theme_owner = models.CharField(max_length=100)

    def __str__(self):
        return self.team


class Department(models.Model):
    department_name = models.CharField(max_length=8)

    def __str__(self):
        return self.department_name


class Group(models.Model):
    group_name = models.CharField(max_length=11)

    def __str__(self):
        return self.group_name


class ZI_Organisation(models.Model):
    zi_organisation_name = models.CharField(max_length=5)

    def __str__(self):
        return self.zi_organisation_name


class TF_Application(models.Model):
    application_name = models.CharField(max_length=100)
    color = models.CharField(default="hsl(0, 100, 100)",max_length=25)

    def __str__(self):
        return self.application_name


CHOICES = [(1, ' '), (2, 'K'), (3, 'U')]


class TF(models.Model):
    tf_name = models.CharField(max_length=100)
    tf_description = models.CharField(max_length=300)
    tf_owner_orga = djongomodels.EmbeddedModelField(model_container=Orga)
    tf_application = djongomodels.EmbeddedModelField(model_container=TF_Application)
    criticality = models.CharField(choices=CHOICES, max_length=1)
    highest_criticality_in_AF = models.CharField(choices=CHOICES, max_length=1)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.tf_name


class User_TF(models.Model):
    tf_name = models.CharField(max_length=100)
    model_tf_pk = models.IntegerField()
    on_delete_list = models.BooleanField(default=False)
    color = models.CharField(default="hsl(0, 100, 100)", max_length=25)

    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.tf_name


class GF(models.Model):
    gf_name = models.CharField(max_length=150)
    gf_description = models.CharField(max_length=250)
    tfs = djongomodels.ArrayReferenceField(to=TF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.gf_name


class User_GF(models.Model):
    gf_name = models.CharField(max_length=150)
    model_gf_pk = models.IntegerField()
    tfs = djongomodels.ArrayModelField(model_container=User_TF)
    on_delete_list = models.BooleanField(default=False)

    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.gf_name


class AF(models.Model):
    af_name = models.CharField(max_length=150)
    af_description = models.CharField(max_length=250)
    gfs = djongomodels.ArrayReferenceField(to=GF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.af_name


class User_AF(models.Model):
    af_name = models.CharField(max_length=150)
    model_af_pk = models.IntegerField()
    gfs = djongomodels.ArrayModelField(model_container=User_GF)
    on_delete_list = models.BooleanField(default=False)
    af_applied = models.DateTimeField()
    af_valid_from = models.DateTimeField()
    af_valid_till = models.DateTimeField()

    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.af_name


class Role(models.Model):
    role_name = models.CharField(max_length=150)
    role_description = models.CharField(max_length=250)
    afs = djongomodels.ArrayReferenceField(to=AF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.role_name


class CustomAccountManager(BaseUserManager):
    def create_user(self, identity, password):
        user = self.model(identity=identity, password=password)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False

        if not user.orga:
            user.orga = Orga()
        if not user.group:
            user.group = Group()
        if not user.department:
            user.department = Department()
        if not user.zi_organisation:
            user.zi_organisation = ZI_Organisation()
        if not user.roles:
            user.roles = [Role()]
        if not user.direct_connect_afs:
            user.direct_connect_afs = [AF()]
        if not user.direct_connect_gfs:
            user.direct_connect_gfs = [GF()]
        if not user.direct_connect_tfs:
            user.direct_connect_tfs = [TF()]
        if not user.my_requests:
            user.my_requests = [ChangeRequests()]
        if not user.user_afs:
            user.user_afs = []
        if not user.transfer_list:
            user.transfer_list = []
        if not user.transfer_list:
            user.delete_list = []

        user.save(using=self.db)
        return user

    def create_staff(self, identity, password):
        user = self.create_user(identity=identity, password=password)
        user.is_staff = True
        user.is_superuser = False
        user.save(using=self.db)
        return user

    def create_superuser(self, identity, password):
        user = self.create_user(identity=identity, password=password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user

    def get_by_natural_key(self, identity_):
        case_insensitive_identitiy_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        print(identity_)
        return self.get(**{case_insensitive_identitiy_field: identity_})


class User(AbstractUser):
    identity = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)
    orga = djongomodels.EmbeddedModelField(model_container=Orga)
    department = djongomodels.EmbeddedModelField(model_container=Department)
    group = djongomodels.EmbeddedModelField(model_container=Group)
    zi_organisation = djongomodels.EmbeddedModelField(model_container=ZI_Organisation)
    roles = djongomodels.ArrayReferenceField(to=Role, on_delete=models.CASCADE)
    direct_connect_afs = djongomodels.ArrayReferenceField(to=AF, on_delete=models.CASCADE)
    direct_connect_gfs = djongomodels.ArrayReferenceField(to=GF, on_delete=models.CASCADE)
    direct_connect_tfs = djongomodels.ArrayReferenceField(to=TF, on_delete=models.CASCADE)
    my_requests = djongomodels.ArrayReferenceField(to=ChangeRequests, on_delete=models.CASCADE)
    user_afs = djongomodels.ArrayModelField(model_container=User_AF)
    transfer_list = djongomodels.ArrayModelField(model_container=User_AF)
    delete_list = djongomodels.ArrayModelField(model_container=User_AF)
    is_staff = models.BooleanField(default=False)
    password = models.CharField(max_length=32)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'identity'

    objects = CustomAccountManager()

    def natural_key(self):
        return self.identity

    def get_short_name(self):
        return self.identity

    def __str__(self):
        return self.identity


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

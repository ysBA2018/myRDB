import csv
import json
import re

from json2html import *
import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
import datetime

# from django_filters.rest_framework import DjangoFilterBackend
# from mongoengine import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .filters import UserFilter
from .forms import CustomUserCreationForm, SomeForm
from .models import Role, AF, GF, TF, Orga, Group, Department, ZI_Organisation, TF_Application, User_AF, User_TF, \
    User_GF
from rest_framework import viewsets
from .serializers import UserSerializer, RoleSerializer, AFSerializer, GFSerializer, TFSerializer, OrgaSerializer, \
    GroupSerializer, DepartmentSerializer, ZI_OrganisationSerializer, TF_ApplicationSerializer, UserListingSerializer, \
    CompleteUserListingSerializer, UserModelRightsSerializer
from django.views import generic

from django.contrib.auth import get_user_model

User = get_user_model()


class CSVtoMongoDB(generic.FormView):
    template_name = 'myRDB/csvToMongo.html'
    form_class = SomeForm
    success_url = '#'

    def form_valid(self, form):
        self.start_import_action()
        return super().form_valid(form)

    def start_import_action(self):
        firstline = True
        # TODO: dateiimportfield und pfad müssen noch verbunden werden!
        with open("myRDB_app/static/myRDB/data/Aus IIQ - User und TF komplett Neu_20180817.csv") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            cur_val = 0
            for line in csvreader:
                if firstline == True:
                    firstline = False
                    pass
                else:
                    print(line)
                    orga = None
                    try:
                        orga = Orga.objects.get(team=line[8])
                    except(KeyError, Orga.DoesNotExist):
                        orga = Orga(team=line[8])
                    orga.save()

                    tf_application = None
                    try:
                        tf_application = TF_Application.objects.get(application_name=line[9])
                    except(KeyError, TF_Application.DoesNotExist):
                        right_color = "hsl(%d, 50%%, 50%%)" % cur_val
                        tf_application = TF_Application(application_name=line[9], color=right_color)
                        cur_val = (cur_val + 20) % 355

                    tf_application.save()

                    tf = None
                    try:
                        tf = TF.objects.get(tf_name=line[3])
                    except(KeyError, TF.DoesNotExist):
                        tf = TF(tf_name=line[3], tf_description=line[4], highest_criticality_in_AF=line[7],
                                tf_owner_orga=orga, tf_application=tf_application, criticality=line[10])
                    tf.save()

                    gf = None
                    try:
                        gf = GF.objects.get(gf_name=line[11])
                    except(KeyError, GF.DoesNotExist):
                        gf = GF(gf_name=line[11], gf_description=line[12])
                        gf.save()
                    gf.tfs.add(tf)
                    gf.save()

                    af = None
                    try:
                        af = AF.objects.get(af_name=line[5])
                    except(KeyError, AF.DoesNotExist):
                        # TODO: Daten werden noch nicht korreckt eingetragen -> immer Null

                        if line[15] == "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6])
                        if line[15] != "" and line[16] == "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] == "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                                    , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat())
                        if line[15] != "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6],
                                    af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat(),
                                    af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat(),
                                    af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] != "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                                    , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                        if line[15] == "" and line[16] == "" and line[17] != "":
                            af = AF(af_name=line[5], af_description=line[6]
                                    , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
                    af.save()
                    af.gfs.add(gf)

                    user = None
                    try:
                        user = User.objects.get(identity=line[0])
                        if user.name != line[1]:
                            user.name = line[1]
                        if user.first_name != line[2]:
                            user.first_name = line[2]
                        if user.username != line[0]:
                            user.username = line[0]
                    except(KeyError, User.DoesNotExist):
                        user = User(identity=line[0], name=line[1], first_name=line[2], username=line[0])
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
                        if not user.user_afs:
                            user.user_afs = []
                        if not user.transfer_list:
                            user.transfer_list = []
                    if user.user_afs.__len__() == 0:
                        user_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk, color=tf_application.color)
                        user_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[])
                        user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[])
                        user_gf.tfs.append(user_tf)
                        user_af.gfs.append(user_gf)
                        user.user_afs.append(user_af)
                    else:
                        afcount = 0
                        for uaf in user.user_afs:
                            if uaf.af_name != af.af_name:
                                afcount += 1
                            else:
                                gfcount = 0
                                for ugf in uaf.gfs:
                                    if ugf.gf_name != gf.gf_name:
                                        gfcount += 1
                                    else:
                                        tfcount = 0
                                        for utf in ugf.tfs:
                                            if utf.tf_name != tf.tf_name:
                                                tfcount += 1
                                            else:
                                                break
                                        if tfcount == ugf.tfs.__len__():
                                            ugf.tfs.append(User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                   color=tf_application.color))
                                if gfcount == uaf.gfs.__len__():
                                    uaf.gfs.append(User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                                           tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                        color=tf_application.color)]))
                        if afcount == user.user_afs.__len__():
                            user.user_afs.append(User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[
                                User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                        tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                     color=tf_application.color)])]))

                    user.direct_connect_afs.add(af)
                    user.save()


class Login(generic.TemplateView):
    template_name = 'myRDB/registration/login.html'


class Logout(generic.TemplateView):
    template_name = 'myRDB/registration/logout.html'


class Register(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = '/myRDB/login'
    template_name = 'myRDB/registration/register.html'


class Password_Reset(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_form.html'


class Password_Reset_Done(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_done.html'


class Password_Reset_Confirm(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_confirm.html'


class Password_Reset_Complete(generic.TemplateView):
    template_name = 'myRDB/registration/password_reset_complete.html'


class IndexView(generic.ListView):
    template_name = 'myRDB/index.html'
    queryset = User.objects.all()

    def get_queryset(self):
        logged_in_user = self.request.user
        return Response({'user': logged_in_user})


class Search_All(generic.ListView):
    template_name = 'myRDB/search_all.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/searchlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas', 'tf_applications', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 20
        else:
            self.paginate_by = 20
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params

        if not self.extra_context.keys().__contains__('data') or changed == True:
            res = requests.get(url, headers=headers)
            user_json_data = res.json()
            self.extra_context['data'] = self.prepare_table_data(user_json_data, headers)
        self.extra_context['params_for_pagination'] = params
        return self.extra_context['data']

        # table=json2html.convert(json=user_json_data['results'])
        # print(table)
        # return Response(data=user_json_data, content_type='application/html')

    def prepare_table_data(self, json_data, headers):
        lines = []

        url = 'http://127.0.0.1:8000/tfs/'
        res = requests.get(url, headers=headers)
        tf_json_data = res.json()
        for user in json_data['results']:
            for af in user['user_afs']:
                if self.request.GET.keys().__contains__('af_name'):
                    if not af['af_name'].__contains__(self.request.GET['af_name']):
                        continue
                for gf in af['gfs']:
                    if self.request.GET.keys().__contains__('gf_name'):
                        if not gf['gf_name'].__contains__(self.request.GET['gf_name']):
                            continue
                    for tf in gf['tfs']:
                        if self.request.GET.keys().__contains__('tf_name'):
                            if not tf['tf_name'].__contains__(self.request.GET['tf_name']):
                                continue
                        model_tf = [x for x in tf_json_data['results'] if x['pk'] == tf['model_tf_pk']].pop(0)
                        line = [user['identity'], user['name'], user['first_name'], tf['tf_name'], gf['gf_name'],
                                af['af_name'],
                                model_tf['tf_owner_orga']['team'],
                                model_tf['tf_application']['application_name'], model_tf['tf_description'], '',
                                user['deleted']]
                        if self.extra_context.keys().__contains__(
                                'tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga'] and \
                                    model_tf['tf_application']['application_name'] == self.request.GET[
                                'tf_application']:
                                lines.append(line)
                        elif self.extra_context.keys().__contains__(
                                'tf_owner_orga') and not self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga']:
                                lines.append(line)
                        elif not self.extra_context.keys().__contains__(
                                'tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_application']['application_name'] == self.request.GET['tf_application']:
                                lines.append(line)
                        else:
                            lines.append(line)
        return lines


class Users(generic.ListView):
    template_name = 'myRDB/users.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/userlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 10
        else:
            self.paginate_by = 10
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params
        self.extra_context['params_for_pagination'] = params

        if changed == True or not self.extra_context.keys().__contains__('paginated_users'):
            res = requests.get(url, headers=headers)
            user_json_data = res.json()
            # user_count= user_json_data['count']
            users = {'users': user_json_data['results']}
            self.extra_context['paginated_users'] = users
        else:
            users = self.extra_context['paginated_users']
        response = Response(users)
        print(response.data['users'])

        user_paginator = Paginator(response.data['users'], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            user_paged_data = user_paginator.page(page)
        except PageNotAnInteger:
            user_paged_data = user_paginator.page(1)
        except EmptyPage:
            user_paged_data = user_paginator.page(user_paginator.num_pages)

        self.extra_context['paged_data'] = user_paged_data
        return response.data['users']


def populate_choice_fields(headers, field):
    url = 'http://127.0.0.1:8000/' + field + '/'
    res = requests.get(url, headers=headers)
    json_data = res.json()
    results = {field: json_data['results']}
    response = Response(results)
    return response.data[field]


def build_url_params(request, extra_context):
    params = ""
    changed = False
    if 'userSearch' in request.GET:
        user_search = request.GET['userSearch']
        search_what = request.GET['search_what']
        if extra_context.keys().__contains__("user_search"):
            if user_search != extra_context["user_search"] or search_what != extra_context["search_what"]:
                changed = True
        else:
            changed = True
        extra_context["userSearch"] = user_search
        extra_context["search_what"] = search_what
        params = "?userSearch=" + user_search + "&search_what=" + search_what
    if 'zi_organisation' in request.GET:
        zi_organisation = '----'
        if not request.GET['zi_organisation'] == '----':
            zi_organisation = request.GET['zi_organisation']
            params = params + "&zi_organisation=" + zi_organisation
        if extra_context.keys().__contains__("zi_organisation"):
            if zi_organisation != extra_context["zi_organisation"]:
                changed = True
        else:
            changed = True
        extra_context["zi_organisation"] = zi_organisation
    if 'department' in request.GET:
        department = '----'
        if not request.GET['department'] == '----':
            department = request.GET['department']
            params = params + "&department=" + department
        if extra_context.keys().__contains__("department"):
            if department != extra_context["department"]:
                changed = True
        else:
            changed = True
        extra_context["department"] = department
    if 'orga' in request.GET:
        orga = '----'
        if not request.GET['orga'] == '----':
            orga = request.GET['orga']
            params = params + "&orga=" + orga
        if extra_context.keys().__contains__("orga"):
            if orga != extra_context["orga"]:
                changed = True
        else:
            changed = True
        extra_context["orga"] = orga
    if 'tf_owner_orga' in request.GET:
        tf_owner_orga = '----'
        if not request.GET['tf_owner_orga'] == '----':
            tf_owner_orga = request.GET['tf_owner_orga']
            params = params + "&tf_owner_orga=" + tf_owner_orga
        if extra_context.keys().__contains__("tf_owner_orga"):
            if tf_owner_orga != extra_context["tf_owner_orga"]:
                changed = True
        else:
            changed = True
        extra_context["tf_owner_orga"] = tf_owner_orga
    if 'tf_application' in request.GET:
        tf_application = '----'
        if not request.GET['tf_application'] == '----':
            tf_application = request.GET['tf_application']
            params = params + "&tf_application=" + tf_application
        if extra_context.keys().__contains__("tf_application"):
            if tf_application != extra_context["tf_application"]:
                changed = True
        else:
            changed = True
        extra_context["tf_application"] = tf_application
    if 'role' in request.GET:
        role = '----'
        if not request.GET['role'] == '----':
            role = request.GET['role']
            params = params + "&role=" + role
        if extra_context.keys().__contains__("role"):
            if role != extra_context["role"]:
                changed = True
        else:
            changed = True
        extra_context["role"] = role
    if 'group' in request.GET:
        group = '----'
        if not request.GET['group'] == '----':
            group = request.GET['group']
            params = params + "&group=" + group
        if extra_context.keys().__contains__("group"):
            if group != extra_context["group"]:
                changed = True
        else:
            changed = True
        extra_context["group"] = group
    if 'af_name' in request.GET:
        af_name = ''
        if not request.GET['af_name'] == '':
            af_name = request.GET['af_name']
            params = params + "&af_name=" + af_name
        if extra_context.keys().__contains__("af_name"):
            if af_name != extra_context["af_name"]:
                changed = True
        else:
            changed = True
        extra_context["af_name"] = af_name
    if 'gf_name' in request.GET:
        gf_name = ''
        if not request.GET['gf_name'] == '':
            gf_name = request.GET['gf_name']
            params = params + "&gf_name=" + gf_name
        if extra_context.keys().__contains__("gf_name"):
            if gf_name != extra_context["gf_name"]:
                changed = True
        else:
            changed = True
        extra_context["gf_name"] = gf_name
    if 'tf_name' in request.GET:
        tf_name = ''
        if not request.GET['tf_name'] == '':
            tf_name = request.GET['tf_name']
            params = params + "&tf_name=" + tf_name
        if extra_context.keys().__contains__("tf_name"):
            if tf_name != extra_context["tf_name"]:
                changed = True
        else:
            changed = True
        extra_context["tf_name"] = tf_name

    return params, changed


class Compare(generic.ListView):
    model = User
    template_name = 'myRDB/compare/compare.html'
    # paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compareUserIdentity = self.request.GET['user_search']
        print(compareUserIdentity)

        # TODO: hier noch lösung mit Params über API finden!
        compareUser = User.objects.get(identity=compareUserIdentity)

        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/users/%d' % compareUser.pk
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        res = requests.get(url, headers=headers)
        user_json_data = res.json()

        user_json_data, scatterData = prepareJSONdata(compareUserIdentity, user_json_data, True, headers)

        compUserRoles = user_json_data['roles']
        compUserAfs = user_json_data['children']

        data, comp_gf_count, comp_tf_count = prepareTableData(compareUser, compUserRoles, compUserAfs, headers)

        context['comp_role_count'] = len(compUserRoles)
        context['comp_af_count'] = len(compUserAfs)
        context['comp_gf_count'] = comp_gf_count
        context['comp_tf_count'] = comp_tf_count
        context["compareUser"] = compareUser
        context["compareUser_table_data"] = data
        context["compareUser_graph_data"] = user_json_data

        return context

    def get_queryset(self):
        self.extra_context['current_site'] = "compare"
        setViewMode(self.request, self.extra_context)
        if not "user_identity" in self.request.GET.keys():
            user = self.request.user
            self.extra_context['identity_param'] = None
        else:
            # TODO: hier noch lösung mit Params über API finden!
            user = User.objects.get(identity=self.request.GET['user_identity'])
            self.extra_context['identity_param'] = self.request.GET['user_identity']

        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/users/%d' % user.pk
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        res = requests.get(url, headers=headers)
        user_json_data = res.json()

        userid = user.id
        roles = user_json_data['roles']
        print(userid, user)

        user_json_data, scatterData = prepareJSONdata(user.identity, user_json_data, False, headers)

        delete_list, delete_list_with_category = build_up_delete_list(user_json_data)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        self.extra_context['delete_list_table_data'] = delete_list_table_data
        self.extra_context['delete_list_count'] = delete_list_count
        self.extra_context['delete_list'] = {"children": delete_list}

        transfer_list = user_json_data['transfer_list']
        # self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        # self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['transfer_list'] = {"children": transfer_list}

        user_json_data = update_user_data(user_json_data, delete_list_with_category)
        self.extra_context['jsondata'] = user_json_data
        afs = user_json_data['children']

        data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)

        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')

        return data


class ProfileRightsAnalysis(generic.ListView):
    model = User
    template_name = 'myRDB/profile/profile_rights_analysis.html'
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "analysis"

        user_data = self.request.session.get('user_data')
        table_data = self.request.session.get('table_data')

        if self.request.GET.keys().__contains__("level"):
            self.extra_context['level'] = self.request.GET['level']
        else:
            self.extra_context['level'] = 'AF'
        logged_in_user_token = self.request.user.auth_token
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        equalRights = []
        unequalRights = []
        equalModelRights = []
        unequalModelRights = []
        equalRightsStats = []
        unequalRightsStats = []

        if self.extra_context['level'] == "AF":
            afs = sorted(user_data['children'], key=lambda k: k['name'])
            model_afs = iter(sorted(get_user_model_rights_by_key(user_data['pk'], headers)['direct_connect_afs'],
                                    key=lambda k: k['af_name']))

            for af in afs:
                # if af['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while True:
                    current_model = next(model_afs)
                    if af['name'] == current_model['af_name']:
                        stats = {}
                        stats['right_name'] = current_model['af_name']
                        stats['description'] = current_model['af_description']
                        self.prepareModelJSONdata(current_model, True, False, headers)
                        equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                            af,
                            current_model,
                            equalRights,
                            unequalRights,
                            equalModelRights,
                            unequalModelRights,
                            True,
                            False,
                            stats,
                            unequalRightsStats,
                            equalRightsStats)
                        break

                # else:
                #    afs.remove(af)
        elif self.extra_context['level'] == "GF":
            afs = user_data['children']
            gfs = []
            for af in afs:
                for gf in af['children']:
                    gfs.append(gf)
            gfs = sorted(gfs, key=lambda k: k['name'])

            model_afs = get_user_model_rights_by_key(user_data['pk'], headers)['direct_connect_afs']
            model_gfs = []
            for af in model_afs:
                for gf in af['gfs']:
                    model_gfs.append(gf)
            model_gfs = iter(sorted(model_gfs, key=lambda k: k['gf_name']))

            for gf in gfs:
                # if gf['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while True:
                    current_model = next(model_gfs)
                    if gf['name'] == current_model['gf_name']:
                        stats = {}
                        stats['right_name'] = current_model['gf_name']
                        stats['description'] = current_model['gf_description']
                        self.prepareModelJSONdata(current_model, False, True, headers)
                        equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                            gf,
                            current_model,
                            equalRights,
                            unequalRights,
                            equalModelRights,
                            unequalModelRights,
                            False,
                            True,
                            stats,
                            unequalRightsStats,
                            equalRightsStats)

                        break

                # else:
                #    gfs.remove(gf)

        self.extra_context['equal_rights'] = sorted(equalRights, key=lambda k: k['name'])
        self.extra_context['unequal_rights'] = sorted(unequalRights, key=lambda k: k['name'])
        self.extra_context['equal_model_rights'] = sorted(equalModelRights, key=lambda k: k['name'])
        self.extra_context['unequal_model_rights'] = sorted(unequalModelRights, key=lambda k: k['name'])
        self.extra_context['equal_rights_stats'] = sorted(equalRightsStats, key=lambda k: k['right_name'])
        self.extra_context['unequal_rights_stats'] = sorted(unequalRightsStats, key=lambda k: k['right_name'])

        self.extra_context['user_identity'] = user_data['identity']
        self.extra_context['user_first_name'] = user_data['first_name']
        self.extra_context['user_name'] = user_data['name']
        self.extra_context['user_department'] = user_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')
        return None

    def compareRightToModel(self, userRight, compareModel, equalRights, unequalRights, equalModelRights,
                            unequalModelRights, isAF, isGF, stats, unequalRightsStats, equalRightsStats):
        equal = False
        equalGFSum = 0
        equalTFSum = 0

        tf_count = 0
        model_tf_count = 0
        tf_count_diff = 0

        if isAF:
            modelGFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

            gf_count = len(userRight['children'])
            model_gf_count = len(compareModel['children'])
            gf_count_diff = model_gf_count - gf_count

            stats['gf_count'] = gf_count
            stats['model_gf_count'] = model_gf_count
            stats['gf_count_diff'] = gf_count_diff

            for gf in sorted(userRight['children'], key=lambda k: k['name']):
                currentGFModel = next(modelGFIter)
                if gf['name'] == currentGFModel['name']:
                    equalGFSum += 1
                modelTFIter = iter(sorted(currentGFModel['children'], key=lambda k: k['name']))

                model_tf_count += len(currentGFModel['children'])
                tf_count += len(gf['children'])
                tf_count_diff = model_tf_count - tf_count

                for tf in sorted(gf['children'], key=lambda k: k['name']):
                    currentTFModel = next(modelTFIter)
                    if tf['name'] == currentTFModel['name']:
                        equalTFSum += 1
            if equalGFSum == gf_count and equalTFSum == tf_count and gf_count_diff == 0 and tf_count_diff == 0:
                equal = True
        if isGF:
            modelTFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

            model_tf_count += len(compareModel['children'])
            tf_count += len(userRight['children'])
            tf_count_diff = model_tf_count - tf_count

            for tf in sorted(userRight['children'], key=lambda k: k['name']):
                currentTFModel = next(modelTFIter)
                if tf['name'] == currentTFModel['name']:
                    equalTFSum += 1
            if equalTFSum == tf_count and tf_count_diff == 0:
                equal = True

        stats['tf_count'] = tf_count
        stats['model_tf_count'] = model_tf_count
        stats['tf_count_diff'] = tf_count_diff

        if equal:
            equalModelRights.append(compareModel)
            equalRights.append(userRight)
            equalRightsStats.append(stats)
        else:
            unequalModelRights.append(compareModel)
            unequalRights.append(userRight)
            unequalRightsStats.append(stats)
        return equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats

    def prepareModelJSONdata(self, json_data, is_af, is_gf, headers):
        print(type(json_data), json_data)
        if is_af:
            json_data["name"] = json_data.pop('af_name')
            json_data["children"] = json_data.pop('gfs')
            for gf in json_data['children']:
                gf["name"] = gf.pop('gf_name')
                gf["children"] = gf.pop('tfs')
                for tf in gf['children']:
                    tf["name"] = tf.pop('tf_name')
                    tf["size"] = 2000
        if is_gf:
            json_data["name"] = json_data.pop('gf_name')
            json_data["children"] = json_data.pop('tfs')
            for tf in json_data['children']:
                tf["name"] = tf.pop('tf_name')
                tf["size"] = 2000


class Profile(generic.ListView):
    model = User
    template_name = 'myRDB/profile/profile.html'
    # paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "profile"

        setViewMode(self.request, self.extra_context)

        if not "identity" in self.request.GET.keys():
            user = self.request.user
            self.extra_context['identity_param'] = None
        else:
            # TODO: hier noch lösung mit Params über API finden!
            user = User.objects.get(identity=self.request.GET['identity'])
            self.extra_context['identity_param'] = self.request.GET['identity']

        logged_in_user_token = self.request.user.auth_token
        url = 'http://127.0.0.1:8000/users/%d' % user.pk
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        res = requests.get(url, headers=headers)
        user_json_data = res.json()

        userid = user.id
        roles = user_json_data['roles']
        print(userid, user)

        user_json_data, scatterData = prepareJSONdata(user.identity, user_json_data, False, headers)
        self.extra_context['scatterData'] = scatterData

        delete_list, delete_list_with_category = build_up_delete_list(user_json_data)
        del_af_count, del_gf_count, del_tf_count = get_delete_list_counts(delete_list_with_category)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        # self.extra_context['delete_list_table_data'] = get_extra_paginator("delete_list",delete_list_table_data,self.request)
        self.extra_context['delete_list_table_data'] = delete_list_table_data
        self.extra_context['delete_list_count'] = delete_list_count
        self.extra_context['delete_list'] = {"children": delete_list}

        user_json_data = update_user_data(user_json_data, delete_list_with_category)

        afs = user_json_data['children']
        data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)

        self.request.session['user_data'] = user_json_data
        '''
        self.request.session['table_data'] = data
        self.request.session['delete_list_graph_data'] = {"children":delete_list}
        self.request.session['delete_list_table_data'] = delete_list_table_data
        self.request.session['delete_list_count'] = delete_list_count
        '''
        self.extra_context['role_count'] = len(roles)
        self.extra_context['af_count'] = len(afs) + del_af_count
        self.extra_context['gf_count'] = gf_count + del_gf_count
        self.extra_context['tf_count'] = tf_count + del_tf_count

        self.extra_context['jsondata'] = user_json_data
        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.request.session['role_count'] = len(roles)
        self.request.session['af_count'] = len(afs) + del_af_count
        self.request.session['gf_count'] = gf_count + del_gf_count
        self.request.session['tf_count'] = tf_count + del_tf_count

        return data


def get_delete_list_counts(list):
    del_af_count = 0
    del_gf_count = 0
    del_tf_count = 0
    for right in list:
        if right['type'] == 'af':
            af = right['right']
            del_af_count += 1
            gfs = af['children']
            del_gf_count += len(gfs)
            for gf in gfs:
                tfs = gf['children']
                del_tf_count += len(tfs)
        elif right['type'] == "gf":
            gf = right['right']
            del_gf_count += 1
            tfs = gf['children']
            del_tf_count += len(tfs)
        elif right['type'] == "tf":
            del_tf_count += 1

    return del_af_count, del_gf_count, del_tf_count


'''
    def autocompleteModel(self, request):
        if request.is_ajax():
            q = request.GET.get('term', '').capitalize()
            search_qs = User.objects.filter(name__startswith=q)
            results = []
            print(q)
            for r in search_qs:
                results.append(r.FIELD)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
'''


def get_extra_paginator(identifyer, list, request):
    extra_paginator = Paginator(list, 3)
    page = request.GET.get(identifyer + '_page')

    try:
        list_data = extra_paginator.page(page)
    except PageNotAnInteger:
        list_data = extra_paginator.page(1)
    except EmptyPage:
        list_data = extra_paginator.page(extra_paginator.num_pages)

    return list_data


def setViewMode(request, extra_context):
    if request.GET.keys().__contains__("view_mode"):
        extra_context['view_mode'] = request.GET['view_mode']
    else:
        extra_context['view_mode'] = 'Graphische Ansicht'


def prepareTrashTableData(afs):
    tfList = []
    gfList = []
    afList = []

    for af in afs:
        if af.keys().__contains__('parent') and af.keys().__contains__('grandparent'):
            # wegen löschliste-tabelle: af hat keine kinder aber parent & grandparent-key -> af ist einzelne tf
            tfList.append(af['name'])
            gfList.append(af['parent'])
            afList.append(af['grandparent'])
        elif af.keys().__contains__('parent') and not af.keys().__contains__('grandparent'):
            # wegen löschliste-tabelle: af hat nur parent aber kein grandparent -> af ist gf
            gfs = af['children']
            for gf in gfs:
                tfList.append(gf['name'])
                gfList.append(af['name'])
                afList.append(af['parent'])
        else:
            gfs = af['children']
            for gf in gfs:
                tfs = gf['children']
                for tf in tfs:
                    tfList.append(tf['name'])
                    gfList.append(gf['name'])
                    afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    lis_data = list(data)
    return lis_data, len(lis_data)


def prepareTableData(user, roles, afs, headers):
    tfList = []
    gfList = []
    afList = []
    gf_count = 0
    for af in afs:
        gfs = af['children']
        gf_count += len(gfs)
        for gf in gfs:
            tfs = gf['children']
            for tf in tfs:
                tfList.append(tf['name'])
                gfList.append(gf['name'])
                afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    tf_count = len(tfList)
    return list(data), gf_count, tf_count


def get_af_by_key(pk, headers):
    url = 'http://127.0.0.1:8000/afs/%d' % pk
    res = requests.get(url, headers=headers)
    af_json = res.json()
    return af_json


def get_gf_by_key(pk, headers):
    url = 'http://127.0.0.1:8000/gfs/%d' % pk
    res = requests.get(url, headers=headers)
    gf_json = res.json()
    return gf_json


def get_tf_by_key(pk, headers):
    url = 'http://127.0.0.1:8000/tfs/%d' % pk
    res = requests.get(url, headers=headers)
    tf_json = res.json()
    return tf_json


def get_user_model_rights_by_key(pk, headers):
    url = 'http://127.0.0.1:8000/usermodelrights/%d' % pk
    res = requests.get(url, headers=headers)
    gf_json = res.json()
    return gf_json


def get_by_url(url, headers):
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def prepareJSONdata(identity, user_json_data, compareUser, headers):
    print(type(user_json_data), user_json_data)
    user_json_data['children'] = user_json_data.pop('user_afs')
    scatterData = []

    i = 1
    used_colors = {}
    for af in user_json_data['children']:
        # TODO: hier auftrennung delete-graph-jeson-data und user-rights-json-data <-> if berechtigung['on_delete_list']==True
        af['name'] = af.pop('af_name')
        af['children'] = af.pop('gfs')
        model_af = get_af_by_key(pk=af['model_af_pk'], headers=headers)
        if model_af['af_applied'] is None:
            af_applied = ""
        else:
            af_applied = model_af['af_applied']
        for gf in af['children']:
            gf['name'] = gf.pop('gf_name')
            gf['children'] = gf.pop('tfs')
            for tf in gf['children']:
                tf['name'] = tf.pop('tf_name')
                tf['size'] = 3000

                # TODO: scatter-graph für zugewiesen, auf delete-list gesetzt, gelöscht
                scatterData.append({"name": tf['name'], "af_applied": af_applied, "color": tf['color']})

    if not compareUser:
        scatterData.sort(key=lambda r: r["af_applied"])
        i = 0
        for e in scatterData:
            e["index"] = i
            i += 1

    return user_json_data, scatterData


def build_up_delete_list(user_json_data):
    delete_list = []
    delete_list_with_category = []
    rights = user_json_data['children']
    for right in rights:
        if right['on_delete_list']:
            delete_list_with_category.append({"right": right, "type": "af"})
            delete_list.append(right)
        else:
            rights_lev_2 = right['children']
            for right_lev_2 in rights_lev_2:
                if right_lev_2['on_delete_list']:
                    right_lev_2['parent'] = right['name']
                    delete_list_with_category.append({"right": right_lev_2, "type": "gf"})
                    delete_list.append(right_lev_2)
                else:
                    rights_lev_3 = right_lev_2['children']
                    for right_lev_3 in rights_lev_3:
                        if right_lev_3['on_delete_list']:
                            right_lev_3['grandparent'] = right['name']
                            right_lev_3['parent'] = right_lev_2['name']
                            delete_list_with_category.append({"right": right_lev_3, "type": "tf"})
                            delete_list.append(right_lev_3)

    return delete_list, delete_list_with_category


def update_user_data(user_json_data, delete_list):
    for elem in delete_list:
        if elem["type"] == "af":
            for right in user_json_data['children']:
                if right["name"] == elem["right"]["name"]:
                    user_json_data['children'].remove(right)
                    break
        if elem["type"] == "gf":
            for right in user_json_data['children']:
                if right["name"] == elem["right"]["parent"]:
                    for right_lev_2 in right['children']:
                        if right_lev_2["name"] == elem["right"]["name"]:
                            right['children'].remove(right_lev_2)
                            break
            else:
                continue
            break
        if elem["type"] == "tf":
            for right in user_json_data['children']:
                if right["name"] == elem["right"]["grandparent"]:
                    for right_lev_2 in right['children']:
                        if right_lev_2["name"] == elem["right"]["parent"]:
                            for right_lev_3 in right_lev_2['children']:
                                if right_lev_3["name"] == elem["right"]["name"]:
                                    right_lev_2['children'].remove(right_lev_3)
                                    break
                    else:
                        continue
                    break
            else:
                continue
            break
    return user_json_data


class UserModelRightsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserModelRightsSerializer

    def get_queryset(self):
        return User.objects.all().order_by('name')


class CompleteUserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = CompleteUserListingSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000
        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})

        else:
            return User.objects.all().order_by('name')
        return users


class UserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserListingSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000

        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})
        else:
            return User.objects.all().order_by('name')
        return users


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    page_size = 10

    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = UserFilter

    def get_queryset(self):
        return User.objects.all().order_by('name')


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Roles to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.all()


class AFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AFSerializer

    def get_queryset(self):
        return AF.objects.all()


class GFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GFSerializer

    def get_queryset(self):
        return GF.objects.all()


class TFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TFSerializer

    def get_queryset(self):
        self.paginator.page_size = 5000
        return TF.objects.all()


class OrgaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orgas to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = OrgaSerializer

    def get_queryset(self):
        self.paginator.page_size = 1000
        return Orga.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all()


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Departments to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()


class ZI_OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ZI_Organisations to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ZI_OrganisationSerializer

    def get_queryset(self):
        return ZI_Organisation.objects.all()


class TF_ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF_Applications to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TF_ApplicationSerializer

    def get_queryset(self):
        return TF_Application.objects.all()
# Create your views here.

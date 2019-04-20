import csv
import json
import re

import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime

from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import CustomUserCreationForm, SomeForm, ApplyRightForm, DeleteRightForm, AcceptChangeForm, \
    DeclineChangeForm, CustomAuthenticationForm, ProfileHeaderForm
from .models import Role, AF, GF, TF, Orga, Group, Department, ZI_Organisation, TF_Application, User_AF, User_TF, \
    User_GF, ChangeRequests
from rest_framework import viewsets, status
from .serializers import UserSerializer, RoleSerializer, AFSerializer, GFSerializer, TFSerializer, OrgaSerializer, \
    GroupSerializer, DepartmentSerializer, ZI_OrganisationSerializer, TF_ApplicationSerializer, UserListingSerializer, \
    CompleteUserListingSerializer, UserModelRightsSerializer, ChangeRequestsSerializer
from django.views import generic

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView

User = get_user_model()
docker_container_ip = "172.17.0.3"


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
        #
        with open("myRDB_app/static/myRDB/data/Aus IIQ - User und TF komplett Neu_20180817_abMe.csv",
                  encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            cur_val = 0
            for line in csvreader:
                line = [re.sub(r'\s+', '', e) for e in line]

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
                        af = AF(af_name=line[5], af_description=line[6])

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
                        if not user.my_requests:
                            user.my_requests = [ChangeRequests()]
                        if not user.user_afs:
                            user.user_afs = []
                        if not user.transfer_list:
                            user.transfer_list = []
                        if not user.delete_list:
                            user.delete_list = []
                    if user.user_afs.__len__() == 0:
                        user_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk, color=tf_application.color)
                        user_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[])
                        user_af = self.create_user_af(line, af)
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
                            user_af = self.create_user_af(line, af)
                            user_af.gfs.append(User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                                       tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                    color=tf_application.color)]))
                            user.user_afs.append(user_af)

                    user.direct_connect_afs.add(af)
                    user.save()

    def create_user_af(self, line, af):
        if line[15] == "" and line[16] == "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[])
        if line[15] != "" and line[16] == "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat())
        if line[15] != "" and line[16] != "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat())
        if line[15] != "" and line[16] != "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        if line[15] == "" and line[16] != "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        if line[15] == "" and line[16] == "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        return user_af


class Login(LoginView):
    template_name = 'myRDB/registration/login.html'
    authentication_form = CustomAuthenticationForm


class Logout(LogoutView):
    template_name = 'myRDB/registration/logout.html'


class Register(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = '/myRDB/login'
    template_name = 'myRDB/registration/register.html'


class Password_Reset(PasswordResetView):
    template_name = 'myRDB/registration/password_reset_form.html'


class Password_Reset_Done(PasswordResetDoneView):
    template_name = 'myRDB/registration/password_reset_done.html'


class Password_Reset_Confirm(PasswordResetConfirmView):
    template_name = 'myRDB/registration/password_reset_confirm.html'


class Password_Reset_Complete(PasswordResetCompleteView):
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
        #url = 'http://' + self.request.get_host() + '/searchlistings/'
        url = 'http://' + docker_container_ip + '/searchlistings/'
        headers = get_headers(self.request)
        lis = ['zi_organisations', 'orgas', 'tf_applications', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e, self.request)
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
            user_json_data = get_by_url(url, headers)
            self.extra_context['data'] = self.prepare_table_data(user_json_data, headers)
        self.extra_context['params_for_pagination'] = params
        return self.extra_context['data']

        # table=json2html.convert(json=user_json_data['results'])
        # print(table)
        # return Response(data=user_json_data, content_type='application/html')

    def prepare_table_data(self, json_data, headers):
        lines = []

        tf_json_data = get_tfs(get_headers(self.request), self.request)
        for user in json_data:
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
                        model_tf = [x for x in tf_json_data if x['pk'] == tf['model_tf_pk']].pop(0)
                        line = [user['identity'], user['name'], user['first_name'], tf['tf_name'], gf['gf_name'],
                                af['af_name'],
                                model_tf['tf_owner_orga']['team'],
                                model_tf['tf_application']['application_name'], model_tf['tf_description'], '',
                                user['deleted']]
                        lines.append(line)
                        '''
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
                            '''
        return lines


class Users(generic.ListView):
    template_name = 'myRDB/users.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        #url = 'http://' + self.request.get_host() + '/userlistings/'
        url = 'http://' + docker_container_ip + '/userlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e, self.request)
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
            user_json_data = get_by_url(url, headers=headers)
            # user_count= user_json_data['count']
            users = {'users': user_json_data}
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


def populate_choice_fields(headers, field, request):
    #url = 'http://' + request.get_host() + '/' + field + '/'
    url = 'http://' + docker_container_ip + '/' + field + '/'
    json_data = get_by_url(url,get_headers(request))
    if type(json_data) == list:
        results = {field: json_data}
    if type(json_data) == dict:
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
        if 'user_search' in self.request.GET.keys():
            compareUserIdentity = self.request.GET['user_search']
        else:
            compareUserIdentity = self.request.session.get('user_search')

        self.request.session['user_search'] = compareUserIdentity

        headers = get_headers(self.request)
        user_json_data = get_user_by_key(compareUserIdentity, headers=headers, request=self.request)

        user_json_data, scatterData = prepareJSONdata(compareUserIdentity, user_json_data, True, headers,self.request)

        compUserRoles = user_json_data['roles']
        compUserAfs = user_json_data['children']

        data, comp_gf_count, comp_tf_count = prepareTableData(user_json_data, compUserRoles, compUserAfs, headers)

        context['comp_role_count'] = len(compUserRoles)
        context['comp_af_count'] = len(compUserAfs)
        context['comp_gf_count'] = comp_gf_count
        context['comp_tf_count'] = comp_tf_count
        context["compareUser"] = user_json_data
        context["compareUser_table_data"] = data
        context["compareUser_graph_data"] = user_json_data

        return context

    def get_queryset(self):
        self.extra_context['current_site'] = "compare"
        setViewMode(self.request, self.extra_context)
        if not "user_identity" in self.request.GET.keys():
            user = self.request.user
            self.extra_context['identity_param'] = self.request.session.get('user_identity')
        else:
            # TODO: hier noch lösung mit Params über API finden!
            self.extra_context['identity_param'] = self.request.GET['user_identity']

        self.request.session['user_identity'] = self.extra_context['identity_param']
        logged_in_user_token = self.request.user.auth_token
        headers = get_headers(self.request)
        user_json_data = get_user_by_key(self.extra_context['identity_param'], headers, self.request)

        roles = user_json_data['roles']

        user_json_data, scatterData = prepareJSONdata(user_json_data['identity'], user_json_data, False, headers,self.request)

        transfer_list, transfer_list_with_category = prepareTransferJSONdata(user_json_data['transfer_list'])
        transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
        self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        self.extra_context['transfer_list_count'] = transfer_list_count

        self.extra_context['transferlist'] = {"children": transfer_list}
        delete_list = user_json_data['delete_list']
        delete_list, delete_list_with_category = prepare_delete_list(delete_list)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        self.extra_context['delete_list_table_data'] = delete_list_table_data
        self.extra_context['delete_list_count'] = delete_list_count
        self.extra_context['deletelist'] = {"children": delete_list}

        self.extra_context['jsondata'] = user_json_data
        afs = user_json_data['children']

        data, gf_count, tf_count = prepareTableData(user_json_data, roles, afs, headers)

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
    template_name = 'myRDB/profileRightsAnalysis/profile_rights_analysis.html'
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "analysis"
        setViewMode(self.request, self.extra_context)

        user_data = self.request.session.get('user_data')
        table_data = self.request.session.get('table_data')
        delete_graph_data = self.request.session.get('delete_list_graph_data')
        transfer_graph_data = self.request.session.get('transfer_list_graph_data')
        delete_table_data = self.request.session.get('delete_list_table_data')
        transfer_table_data = self.request.session.get('transfer_list_table_data')
        transfer_list_count = self.request.session.get('transfer_list_count')
        delete_list_count = self.request.session.get('delete_list_count')
        self.extra_context['delete_list_table_data'] = delete_table_data
        self.extra_context['transfer_list_table_data'] = transfer_table_data
        self.extra_context['deletelist'] = delete_graph_data
        self.extra_context['transferlist'] = transfer_graph_data
        self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['delete_list_count'] = delete_list_count

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

        equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats = self.compare_right_and_modelright(
            equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights, unequalRights,
            unequalRightsStats, user_data)

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

    def compare_right_and_modelright(self, equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights,
                                     unequalRights, unequalRightsStats, user_data):
        if self.extra_context['level'] == "AF":
            afs = sorted(user_data['children'], key=lambda k: k['name'])
            for af in afs:
                through = False
                model_afs = iter(
                    sorted(get_user_model_rights_by_key(user_data['pk'], headers, self.request)['direct_connect_afs'],
                           key=lambda k: k['af_name']))
                # if af['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while not through:
                    try:
                        current_model = next(model_afs)
                    except StopIteration:
                        print('model_af stop iteration')
                        through = True
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
                        through = True;
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

            model_afs = get_user_model_rights_by_key(user_data['pk'], headers, self.request)['direct_connect_afs']
            model_gfs = []
            for af in model_afs:
                for gf in af['gfs']:
                    model_gfs.append(gf)
            model_gfs = iter(sorted(model_gfs, key=lambda k: k['gf_name']))

            for gf in gfs:
                through = False
                # if gf['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while not through:
                    try:
                        current_model = next(model_gfs)
                    except StopIteration:
                        print("in GF-StopIteration!")
                        through = True
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
                        through = True
                        break

                # else:
                #    gfs.remove(gf)
        return equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats

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
                try:
                    currentGFModel = next(modelGFIter)
                except StopIteration:
                    print("in StopIteration")
                    break

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
    # model = User
    template_name = 'myRDB/profile/profile.html'
    # paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "profile"
        self.extra_context['profile_header_form'] = ProfileHeaderForm
        setViewMode(self.request, self.extra_context)
        print(self.request.get_host())
        if not "identity" in self.request.GET.keys():
            user = self.request.user
            self.request.session['user_identity'] = user.identity
            user_id = user.identity
            self.extra_context['identity_param'] = user.identity
        else:
            # TODO: hier noch lösung mit Params über API finden!
            self.extra_context['identity_param'] = self.request.GET['identity']
            self.request.session['user_identity'] = self.extra_context['identity_param']
            user_id = self.request.GET['identity']

        headers = get_headers(self.request)
        legend_data = get_tf_applications(headers, self.request)['results']
        sorted_legend_data = sorted(legend_data, key=lambda r: r["application_name"])
        self.extra_context['legendData'] = sorted_legend_data

        user_json_data = get_user_by_key(user_id,headers,self.request)

        roles = user_json_data['roles']

        user_json_data, scatterData = prepareJSONdata(user_json_data['identity'], user_json_data, False, headers,self.request)
        self.extra_context['scatterData'] = scatterData

        transfer_list, transfer_list_with_category = prepareTransferJSONdata(user_json_data['transfer_list'])
        transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
        self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['transferlist'] = {"children": transfer_list}

        delete_list = user_json_data['delete_list']
        delete_list, delete_list_with_category = prepare_delete_list(delete_list)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        self.extra_context['delete_list_table_data'] = delete_list_table_data
        self.extra_context['delete_list_count'] = delete_list_count
        self.extra_context['deletelist'] = {"children": delete_list}
        # user_json_data = update_user_data(user_json_data, delete_list_with_category)

        afs = user_json_data['children']
        data, gf_count, tf_count = prepareTableData(user_json_data, roles, afs, headers)

        self.request.session['user_data'] = user_json_data

        self.request.session['table_data'] = data
        self.request.session['delete_list_graph_data'] = {"children": delete_list}
        self.request.session['delete_list_table_data'] = delete_list_table_data
        self.request.session['delete_list_count'] = delete_list_count
        self.request.session['transfer_list_graph_data'] = {"children": transfer_list}
        self.request.session['transfer_list_table_data'] = transfer_list_table_data
        self.request.session['transfer_list_count'] = transfer_list_count

        self.extra_context['role_count'] = len(roles)
        self.extra_context['af_count'] = len(afs)
        self.extra_context['gf_count'] = gf_count
        self.extra_context['tf_count'] = tf_count

        self.extra_context['jsondata'] = user_json_data
        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.request.session['role_count'] = len(roles)
        self.request.session['af_count'] = len(afs)
        self.request.session['gf_count'] = gf_count
        self.request.session['tf_count'] = tf_count

        return data


class RequestPool(generic.ListView):
    model = ChangeRequests
    template_name = 'myRDB/requestPool/request_pool.html'
    extra_context = {}
    context_object_name = 'list_data'

    def get_queryset(self):
        change_requests_json_data = get_changerequests(get_headers(self.request), self.request)
        print(change_requests_json_data)
        requests_by_users = self.repack_data(change_requests_json_data)
        print(requests_by_users)
        self.extra_context['requesting_users'] = requests_by_users
        self.extra_context['accept_form'] = AcceptChangeForm
        self.extra_context['decline_form'] = DeclineChangeForm
        return []

    def repack_data(self, change_requests):
        list_by_user = []
        for data in change_requests:
            if data['status'] == "unanswered":
                user_dict = {'requesting_user': data['requesting_user'], 'apply_requests': [], 'delete_requests': []}
                if not list_by_user.__contains__(user_dict):
                    list_by_user.append(user_dict)

        for data in change_requests:
            for user in list_by_user:
                if user['requesting_user'] == data['requesting_user']:
                    requesting_user = get_user_by_key(data['requesting_user'],
                                                      headers=get_headers(self.request), request=self.request)
                    if data['status'] == "unanswered":
                        # TODO: xv-nummer als SLUG-Field -> dann url über xvnummer aufrufbar
                        if data['action'] == 'apply':
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['transfer_list'])
                            if right is None:
                                model = None
                            else:
                                model = get_model_right(requesting_user, data['right_type'], right['model_right_pk'],
                                                        self.request)
                            user["apply_requests"].append({'right': right, 'model': model, 'type': data['right_type'],
                                                           'right_name': data['right_name'],
                                                           'reason_for_action': data['reason_for_action'],
                                                           'request_pk': data['pk']})
                        else:
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['delete_list'])
                            if right is None:
                                model = None
                            else:
                                model = get_model_right(requesting_user, data['right_type'], right['model_right_pk'],
                                                    self.request)
                            user["delete_requests"].append({'right': right, 'model': model, 'type': data['right_type'],
                                                            'right_name': data['right_name'],
                                                            'reason_for_action': data['reason_for_action'],
                                                            'request_pk': data['pk']})

        return list_by_user


class MyRequests(generic.ListView):
    model = ChangeRequests
    template_name = 'myRDB/myRequests/my_requests.html'
    extra_context = {}
    context_object_name = "accepted_list"

    def post(self, request, *args, **kwargs):
        print("I'm in my_requests-post")
        return HttpResponseRedirect(self.request.path_info)

    def get_queryset(self):
        self.extra_context['current_site'] = "my_requests"
        if 'user_identity' in self.request.session:
            user_identity = self.request.session.get('user_identity')
        else:
            user_identity = self.request.user.identity
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        user = get_user_by_key(user_identity, get_headers(self.request), self.request)
        request_list = self.get_my_requests(user)
        repacked_request_list = self.repack_list(request_list)
        unanswered_list, accepted_list, declined_list = self.presort(repacked_request_list)
        self.extra_context['declined_list'] = declined_list
        self.extra_context['unanswered_list'] = unanswered_list
        return accepted_list

    def repack_list(self, list):
        repacked_list = []
        for request in list:
            requesting_user = get_user_by_key(request['requesting_user'], headers=get_headers(self.request),
                                              request=self.request)
            if request['action'] == 'apply':
                # TODO: wenn berechtigung auf comp_user oder user seite gelöscht wurde -> zuerst modell-recht anzeigen -> wenn auch gelöscht - dann erst None setzen und damit esatz-circle anzeigen
                if request['status'] == "accepted":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
                elif request['status'] == "declined":
                    compare_user = get_user_by_key(request['compare_user'], headers=get_headers(self.request),
                                                   request=self.request)
                    right = get_right_from_list(compare_user, request['right_type'], request['right_name'],
                                                compare_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(compare_user, request['right_type'], right['model_right_pk'],
                                            self.request)
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['transfer_list'])
                    model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                            self.request)
            if request['action'] == 'delete':
                if request['status'] == "accepted":
                    right = None
                    model = None
                elif request['status'] == "declined":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['delete_list'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                            self.request)
            repacked_list.append({'right': right, 'model': model, 'request': request})
        return repacked_list

    def presort(self, list):
        unanswered_dict = {'apply': [], 'delete': []}
        accepted_dict = {'apply': [], 'delete': []}
        declined_dict = {'apply': [], 'delete': []}
        for request in list:
            if request['request']['status'] == 'unanswered':
                if request['request']['action'] == 'apply':
                    unanswered_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    unanswered_dict['delete'].append(request)
            if request['request']['status'] == 'accepted':
                if request['request']['action'] == 'apply':
                    accepted_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    accepted_dict['delete'].append(request)
            if request['request']['status'] == 'declined':
                if request['request']['action'] == 'apply':
                    declined_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    declined_dict['delete'].append(request)
        return unanswered_dict, accepted_dict, declined_dict

    def get_my_requests(self, user):
        request_list = []
        for request in user['my_requests']:
            request_list.append(get_by_url(request, get_headers(self.request)))
        return request_list


class RightApplication(generic.ListView):
    model = User
    template_name = 'myRDB/rightApplication/right_application.html'
    extra_context = {}
    context_object_name = "list_data"

    def get_queryset(self):
        self.extra_context['current_site'] = "right_application"
        self.extra_context['compare_user'] = self.request.session.get('user_search')
        user_identity = self.request.session.get('user_identity')
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        headers = get_headers(self.request)
        user_json_data = get_user_by_key(user_identity, headers, self.request)

        roles = user_json_data['roles']

        user_json_data, scatterData = prepareJSONdata(user_json_data['identity'], user_json_data, False, headers,self.request)

        transfer_list, transfer_list_with_category = prepareTransferJSONdata(user_json_data['transfer_list'])
        model_transfer_list = get_model_list(transfer_list_with_category, headers, self.request)
        # transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
        # self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        # self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['transfer_list'] = transfer_list
        self.extra_context['stripped_transfer_list'] = [right['right'] for right in transfer_list_with_category]
        print(self.extra_context.get('stripped_transfer_list'))
        self.extra_context['model_transfer_list'] = model_transfer_list
        self.extra_context['transfer_form'] = ApplyRightForm

        delete_list = user_json_data['delete_list']
        delete_list, delete_list_with_category = prepare_delete_list(delete_list)
        model_delete_list = get_model_list(delete_list_with_category, headers, self.request)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        # self.extra_context['delete_list_table_data'] = delete_list_table_data
        # self.extra_context['delete_list_count'] = delete_list_count

        self.extra_context['delete_list'] = delete_list
        self.extra_context['stripped_delete_list'] = [right['right'] for right in delete_list_with_category]
        print(self.extra_context.get('stripped_delete_list'))
        self.extra_context['model_delete_list'] = model_delete_list
        self.extra_context['delete_form'] = DeleteRightForm

        # user_json_data = update_user_data(user_json_data, delete_list_with_category)
        self.extra_context['jsondata'] = user_json_data

        # afs = user_json_data['children']
        # data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)

        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')

        return []


def get_model_right(comp_user, type, pk, request):
    if type == 'AF':
        model = get_af_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('af_description')
    if type == 'GF':
        model = get_gf_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('gf_description')
    if type == 'TF':
        model = get_tf_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('tf_description')
    return model


def get_right_from_list(comp_user, type, right, rights):
    for af in rights:
        if type == 'AF':
            if af['af_name'] == right:
                af['name'] = af.pop('af_name')
                af['children'] = af.pop('gfs')
                af['model_right_pk'] = af.pop('model_af_pk')
                for gf in af['children']:
                    gf['name'] = gf.pop('gf_name')
                    gf['children'] = gf.pop('tfs')
                    for tf in gf['children']:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                return af
        if type == 'GF':
            for gf in af['gfs']:
                if gf['gf_name'] == right:
                    gf['name'] = gf.pop('gf_name')
                    gf['children'] = gf.pop('tfs')
                    gf['model_right_pk'] = gf.pop('model_gf_pk')
                    for tf in gf['children']:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                    return gf
        if type == 'TF':
            for gf in af['gfs']:
                for tf in gf['tfs']:
                    if tf['tf_name'] == right:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                        tf['model_right_pk'] = tf.pop('model_tf_pk')
                        return tf


def get_model_list(transfer_list_with_category, headers, request):
    model_list = []
    for right in transfer_list_with_category:
        model = None
        if right['type'] == 'af':
            model = get_af_by_key(pk=right['right']['model_af_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('af_name')
            model['description'] = model.pop('af_description')
        if right['type'] == 'gf':
            model = get_gf_by_key(pk=right['right']['model_gf_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('gf_name')
            model['description'] = model.pop('gf_description')
        if right['type'] == 'tf':
            model = get_tf_by_key(pk=right['right']['model_tf_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('tf_name')
            model['description'] = model.pop('tf_description')
        model['type'] = right['type'].upper()
        model_list.append(model)
    return model_list


def prepareTransferJSONdata(transfer_json_data):
    transfer_list_with_category = []
    for right in transfer_json_data:
        right["name"] = right.pop('af_name')
        right["children"] = right.pop('gfs')
        for gf in right['children']:
            gf["name"] = gf.pop('gf_name')
            gf["children"] = gf.pop('tfs')
            for tf in gf['children']:
                tf["name"] = tf.pop('tf_name')
                tf["size"] = 2000
                if tf['transfer']:
                    type = 'tf'
                    transfer_list_with_category.append({"right": tf, "type": type})
            if gf['transfer']:
                type = 'gf'
                transfer_list_with_category.append({"right": gf, "type": type})
        if right['transfer']:
            type = 'af'
            transfer_list_with_category.append({"right": right, "type": type})

    return transfer_json_data, transfer_list_with_category


def prepareTransferTabledata(transfer_list):
    tfList = []
    gfList = []
    afList = []
    for af in transfer_list:
        for gf in af['children']:
            for tf in gf['children']:
                tfList.append(tf['name'])
                gfList.append(gf['name'])
                afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    lis_data = list(data)
    return lis_data, len(lis_data)


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


def get_headers(request):
    logged_in_user_token = request.user.auth_token
    headers = {'Authorization': 'Token ' + logged_in_user_token.key}
    return headers


def get_tf_applications(headers, request):
    #url = 'http://' + request.get_host() + '/tf_applications/'
    url = 'http://' + docker_container_ip + '/tf_applications/'
    res = requests.get(url, headers=headers)
    tf_applications_json = res.json()
    return tf_applications_json


def get_af_by_key(pk, headers, request):
    #url = 'http://' + request.get_host() + '/afs/%d' % pk
    url = 'http://' + docker_container_ip + '/afs/%d' % pk
    res = requests.get(url, headers=headers)
    af_json = res.json()
    return af_json


def get_gf_by_key(pk, headers, request):
    #url = 'http://' + request.get_host() + '/gfs/%d' % pk
    url = 'http://' + docker_container_ip + '/gfs/%d' % pk
    res = requests.get(url, headers=headers)
    gf_json = res.json()
    return gf_json


def get_tf_by_key(pk, headers, request):
    #url = 'http://' + request.get_host() + '/tfs/%d' % pk
    url = 'http://' + docker_container_ip + '/tfs/%d' % pk
    res = requests.get(url, headers=headers)
    tf_json = res.json()
    return tf_json


def get_user_model_rights_by_key(pk, headers, request):
    #url = 'http://' + request.get_host() + '/usermodelrights/%d' % pk
    url = 'http://' + docker_container_ip + '/usermodelrights/%d' % pk
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def get_user_by_key(pk, headers, request):
    #url = 'http://' + request.get_host() + '/users/%s' % pk
    url = 'http://' + docker_container_ip + '/users/%s' % pk
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def get_changerequests(headers, request):
    #url = 'http://' + request.get_host() + '/changerequests/'
    url = 'http://' + docker_container_ip + '/changerequests/'
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def get_tfs(headers, request):
    #url = 'http://' + request.get_host() + '/tfs/'
    url = 'http://' + docker_container_ip + '/tfs/'
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def get_by_url(url, headers):
    res = requests.get(url, headers=headers)
    json = res.json()
    return json


def prepareJSONdata(identity, user_json_data, compareUser, headers,request):
    print(type(user_json_data), user_json_data)
    user_json_data['children'] = user_json_data.pop('user_afs')
    scatterData = []

    i = 1
    used_colors = {}
    for af in user_json_data['children']:
        af['name'] = af.pop('af_name')
        af['children'] = af.pop('gfs')
        model_af = get_af_by_key(pk=af['model_af_pk'], headers=headers,request=request)
        af['description'] = model_af['af_description']
        if af['af_applied'] is None:
            af_applied = ""
        else:
            af_applied = af['af_applied']
        for gf in af['children']:
            gf['name'] = gf.pop('gf_name')
            gf['children'] = gf.pop('tfs')
            for tf in gf['children']:
                tf['name'] = tf.pop('tf_name')
                tf['size'] = 3000

                # TODO: scatter-graph für zugewiesen, auf delete-list gesetzt, gelöscht
                scatterData.append(
                    {"name": tf['name'], "gf_name": gf['name'], "af_name": af['name'], "af_applied": af_applied,
                     "color": tf['color']})

    if not compareUser:
        scatterData.sort(key=lambda r: r["af_applied"])
        i = 0
        for e in scatterData:
            e["index"] = i
            i += 1

    return user_json_data, scatterData


def prepare_delete_list(delete_list):
    # TODO: umbauen auf db-delete-list <-> bei lösch-aktion zu del-list hinzufügen <- dann hier nur auslesen und json preparieren
    delete_list_with_category = []

    for right in delete_list:
        right['name'] = right.pop('af_name')
        right['children'] = right.pop('gfs')
        for right_lev_2 in right['children']:
            right_lev_2['name'] = right_lev_2.pop('gf_name')
            right_lev_2['children'] = right_lev_2.pop('tfs')
            for right_lev_3 in right_lev_2['children']:
                right_lev_3['name'] = right_lev_3.pop('tf_name')
                right_lev_3['size'] = 2000
                if right_lev_3['delete']:
                    type = 'tf'
                    delete_list_with_category.append({"right": right_lev_3, "type": type})
            if right_lev_2['delete']:
                type = 'gf'
                delete_list_with_category.append({"right": right_lev_2, "type": type})
        if right['delete']:
            type = 'af'
            delete_list_with_category.append({"right": right, "type": type})

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
    pagination_class = None

    def get_queryset(self):
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
    pagination_class = None

    def get_queryset(self):

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
    lookup_field = 'identity'

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
    pagination_class = None

    def get_queryset(self):
        return TF.objects.all()


class OrgaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orgas to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = OrgaSerializer
    pagination_class = None

    def get_queryset(self):
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


class ChangeRequestsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ChangeRequests to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeRequestsSerializer
    pagination_class = None

    def get_queryset(self):
        return ChangeRequests.objects.all()

    def create(self, request, *args, **kwargs):
        print("In ViewSet-Create")
        data = request.data
        objects_to_change = json.loads(data['objects_to_change'])
        serializer = None
        added_requests = []
        for obj in objects_to_change:
            obj_data = {'requesting_user': data['requesting_user[value]'], 'compare_user': data['compare_user[value]'],
                        'action': obj[0]['value'], 'right_name': obj[1]['value'], 'right_type': obj[2]['value'],
                        'reason_for_action': obj[3]['value']}
            serializer = self.get_serializer(data=obj_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            added_requests.append(serializer.data['pk'])
        headers = self.get_success_headers(serializer.data)
        return Response(json.dumps(added_requests), status=status.HTTP_201_CREATED, headers=headers)
# Create your views here.

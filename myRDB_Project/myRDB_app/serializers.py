import json

from rest_framework import serializers
import copy
from .models import Orga, Department, Group, ZI_Organisation, TF_Application, TF, GF, AF, Role, User, User_GF, User_AF, \
    User_TF, ChangeRequests


class ChangeRequestsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeRequests
        fields = (
            'url', 'pk', 'requesting_user', 'compare_user', 'action', 'right_name',
            'right_type', 'reason_for_action', 'created', 'last_modified', 'status', 'reason_for_decline')

    def update(self, instance, validated_data):
        print("in ChangeRequests Upadate")
        print(self._kwargs)
        data = self._kwargs['data']
        if data['action_type'] == 'decline_request':
            instance = self.decline_request(instance, data)
        if data['action_type'] == 'accept_request':
            instance = self.accept_request(instance)
        instance.save()
        return instance

    def decline_request(self, instance, data):
        instance.status = "declined"
        instance.reason_for_decline = data['reason_for_decline']
        return instance

    def accept_request(self, instance):
        instance.status = "accepted"
        return instance


class OrgaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Orga
        fields = ('url', 'pk', 'team', 'theme_owner')


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department
        fields = ('url', 'pk', 'department_name')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'pk', 'group_name')


class ZI_OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ZI_Organisation
        fields = ('url', 'pk', 'zi_organisation_name')


class TF_ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF_Application
        fields = ('url', 'pk', 'application_name', 'color')


class TFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF
        fields = ('url', 'pk', 'tf_name', 'tf_description', 'tf_owner_orga', 'tf_application', 'criticality',
                  'highest_criticality_in_AF')

    tf_owner_orga = OrgaSerializer()
    tf_application = TF_ApplicationSerializer()


class GFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GF
        fields = ('url', 'pk', 'gf_name', 'gf_description', 'tfs')

    tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='tf-detail')


class AFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AF
        fields = ('url', 'pk', 'af_name', 'af_description', 'gfs')

    gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='gf-detail')


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('url', 'pk', 'role_name', 'role_description', 'afs')

    afs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')


class UserTFSerializer(serializers.Serializer):
    tf_name = serializers.CharField(max_length=150)
    model_tf_pk = serializers.IntegerField()
    color = serializers.CharField(default="hsl(0, 100, 100)", max_length=25)
    transfer = serializers.BooleanField(default=False)
    delete = serializers.BooleanField(default=False)
    requested = serializers.BooleanField(default=False)


class UserGFSerializer(serializers.Serializer):
    gf_name = serializers.CharField(max_length=150)
    model_gf_pk = serializers.IntegerField()
    tfs = UserTFSerializer(many=True, read_only=False)
    transfer = serializers.BooleanField(default=False)
    delete = serializers.BooleanField(default=False)
    requested = serializers.BooleanField(default=False)


class UserAFSerializer(serializers.Serializer):
    af_name = serializers.CharField(max_length=150)
    model_af_pk = serializers.IntegerField()
    af_applied = serializers.DateTimeField()
    af_valid_from = serializers.DateTimeField()
    af_valid_till = serializers.DateTimeField()
    transfer = serializers.BooleanField(default=False)
    delete = serializers.BooleanField(default=False)
    requested = serializers.BooleanField(default=False)
    gfs = UserGFSerializer(many=True, read_only=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'url', 'pk', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
            'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password',
            'user_afs', 'transfer_list', 'my_requests', 'delete_list')
        lookup_field = 'identity'
        extra_kwargs = {
            'url': {'lookup_field': 'identity'}
        }

    roles = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='role-detail')
    direct_connect_afs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='af-detail')
    direct_connect_gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='gf-detail')
    direct_connect_tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='tf-detail')
    my_requests = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='changerequests-detail')
    user_afs = UserAFSerializer(many=True, read_only=True)
    transfer_list = UserAFSerializer(many=True, read_only=False)
    delete_list = UserAFSerializer(many=True, read_only=False)

    orga = OrgaSerializer()
    department = DepartmentSerializer()
    group = GroupSerializer()
    zi_organisation = ZI_OrganisationSerializer()

    def update(self, instance, validated_data):
        print("im in the serializer-update-method")
        print(self._kwargs)
        data = self._kwargs['data']
        if data['action_type'] == 'trash':
            instance = self.add_to_delete_list(instance, data)
        elif data['action_type'] == "restore":
            instance = self.remove_from_delete_list(instance, data)
        elif data['action_type'] == "transfer":
            instance = self.add_to_transfer_list(instance, data)
        elif data['action_type'] == "restore_transfer":
            instance = self.remove_from_transfer_list(instance, data)
        elif data['action_type'] == "add_to_requests":
            instance = self.add_to_my_requests(instance, data)
        elif data['action_type'] == "remove_from_requests":
            instance = self.remove_from_my_requests(instance, data)
        elif data['action_type'] == "reverse_action":
            instance = self.reverse_action(instance, data)
        elif data['action_type'] == "clear_transfer_list_and_delete_list":
            instance = self.clear_transferlist_and_deletelist(instance)
        elif data['action_type'] == "set_rights_as_requested":
            instance = self.set_rights_as_requested(instance, data)
        elif data['action_type'] == "perform_action":
            instance = self.perform_action(instance, data)
        elif data['action_type'] == "decline_action":
            instance = self.decline_action(instance, data)
        elif data['action_type'] == "analysis_transfer":
            instance = self.add_to_transfer_list_from_analysis(instance, data)
        instance.save()

        return instance

    def add_to_transfer_list_from_analysis(self,instance,data):
        print('in add to transfer fom analysis')
        print(data)
        if data['right_type']=='tf':
            tf = TF.objects.get(pk=data['right_pk'])
            new_user_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.pk)), color=tf.tf_application.color,
                                  transfer=True)
            for af in instance.transfer_list:
                if af.af_name == data['grandparent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['parent']:
                            gf.tfs.append(new_user_tf)
                            return instance
                    gf = GF.objects.get(gf_name=data['parent'])
                    help_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[new_user_tf])
                    af.gfs.append(help_gf)
                    return instance
            gf = GF.objects.get(gf_name=data['parent'])
            help_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[new_user_tf])
            af = AF.objects.get(af_name=data['grandparent'])
            help_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[help_gf])
            instance.transfer_list.append(help_af)
            return instance
        if data['right_type']=='gf':
            gf = GF.objects.get(pk=data['right_pk'])
            new_user_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=int(float(gf.pk)), tfs=[])
            for tf_id in gf.tfs_id:
                tf = TF.objects.get(pk=tf_id)
                u_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.pk)), color=tf.tf_application.color,
                                  transfer=True)
                new_user_gf.tfs.append(u_tf)
            for af in instance.transfer_list:
                if af.af_name == data['parent']:
                    af.gfs.append(new_user_gf)
                    return instance
            af = AF.objects.get(af_name=data['parent'])
            help_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[new_user_gf])
            instance.transfer_list.append(help_af)
            return instance

        if data['right_type']=='af':
            af = AF.objects.get(pk=data['right_pk'])
            new_user_af = User_AF(af_name=af.af_name, model_af_pk=int(float(af.pk)), gfs=[])
            for gf_id in af.gfs_id:
                gf = GF.objects.get(pk = gf_id)
                u_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[])
                for tf_id in gf.tfs_id:
                    tf = TF.objects.get(pk=tf_id)
                    u_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.pk)), color=tf.tf_application.color,
                                  transfer=True)
                    u_gf.tfs.append(u_tf)
                new_user_af.gfs.append(u_gf)
            instance.transfer_list.append(new_user_af)
        return instance

    def reverse_action(self, instance, data):
        print("in Reverse_action")
        if data['action'] == 'delete':
            instance = self.restore_after_decline(instance, data, 'delete')
        if data['action'] == 'apply':
            instance = self.restore_after_decline(instance, data, 'apply')

        return instance

    def set_rights_as_requested(self, instance, data):
        print("in set_rights_as_requested")
        objects_to_change = json.loads(data['objects_to_change'])
        for obj in objects_to_change:
            action = obj[0]['value']
            right_name = obj[1]['value']
            right_type = obj[2]['value']

            if action == 'apply':
                list = instance.transfer_list
            else:
                list = instance.delete_list

            if right_type == 'AF':
                for right in list:
                    if right_name == right.af_name:
                        right.requested = True
                        break
            elif right_type == 'GF':
                for right in list:
                    for right_lev_2 in right.gfs:
                        if right_name == right_lev_2.gf_name:
                            right_lev_2.requested = True
                            break
                    else:
                        continue
                    break
            elif right_type == 'TF':
                for right in list:
                    for right_lev_2 in right.gfs:
                        for right_lev_3 in right_lev_2.tfs:
                            if right_name == right_lev_3.tf_name:
                                right_lev_3.requested = True
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    break
        return instance

    def decline_action(self, instance, data):
        print("in perform_action")
        request_data = json.loads(data['request_data'])
        if request_data['action'] == 'apply':
            instance = self.restore_after_decline(instance, request_data, 'apply')
        if request_data['action'] == 'delete':
            instance = self.restore_after_decline(instance, request_data, 'delete')

        return instance

    def restore_after_decline(self, instance, request_data, action):
        print("in restore_after_decline")
        print(request_data)
        if action == 'delete':
            list = instance.delete_list
        else:
            list = instance.transfer_list

        if request_data['right_type'] == 'AF':
            data = {'right_name': request_data['right_name'], 'right_type':request_data['right_type'].lower()}

        elif request_data['right_type'] == 'GF':
            for right in list:
                for gf in right.gfs:
                    if gf.gf_name == request_data['right_name']:
                        data = {'right_name': gf.gf_name, 'parent': right.af_name, 'right_type':request_data['right_type'].lower()}
                        break
                else:
                    continue
                break

        elif request_data['right_type'] == 'TF':
            for right in list:
                for gf in right.gfs:
                    for tf in gf.tfs:
                        if tf.tf_name == request_data['right_name']:
                            data = {'right_name': tf.tf_name, 'parent': gf.gf_name, 'grandparent': right.af_name, 'right_type':request_data['right_type'].lower()}
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
        if action == 'delete':
            if request_data['right_type'] == 'AF':
                instance = self.remove_from_delete_list(instance, {'right_name': request_data['right_name']})
            else:
                instance = self.remove_from_delete_list(instance, {'right_name':right.af_name})
        else:
            instance = self.remove_from_transfer_list(instance, data)

        return instance

    def perform_action(self, instance, data):
        print("in perform_action")
        request_data = json.loads(data['request_data'])
        if request_data['action'] == 'apply':
            instance = self.apply_right(instance, request_data['compare_user'], request_data['right_name'],
                                        request_data['right_type'], request_data['last_modified'])
        if request_data['action'] == 'delete':
            instance = self.delete_right(instance, request_data['right_name'], request_data['right_type'])

        return instance

    # TODO: apply und delete auch für gfs und tfs implementieren
    def apply_right(self, instance, compare_xv_user, right_name, right_type, application_date):
        print("in apply right")
        if right_type == "AF":
            index = 0
            for af in instance.transfer_list:
                if af.af_name == right_name:
                    af.af_applied = application_date
                    instance.user_afs.append(af)
                    instance.direct_connect_afs_id.add(af.model_af_pk)
                    instance.transfer_list.pop(index)
                    break
                index += 1
        if right_type == "GF":
            af_index = 0
            for af in instance.transfer_list:
                index = 0
                for gf in af.gfs:
                    if gf.gf_name == right_name:
                        for u_af in instance.user_afs:
                            if u_af.af_name == af.af_name:
                                u_af.gfs.append(gf)
                                af.gfs.pop(index)
                                break
                    index += 1
                if not af.gfs:
                    instance.transfer_list.pop(af_index)
                    break
                af_index += 1
        if right_type == "TF":
            af_index = 0
            for af in instance.transfer_list:
                gf_index = 0
                for gf in af.gfs:
                    index = 0
                    for tf in gf.tfs:
                        if tf.tf_name == right_name:
                            for u_af in instance.user_afs:
                                if u_af.af_name == af.af_name:
                                    for u_gf in u_af.gfs:
                                        if u_gf.gf_name == gf.gf_name:
                                            u_gf.tfs.append(tf)
                                            gf.tfs.pop(index)
                                            break
                        index += 1
                    if not gf.tfs:
                        af.gfs.pop(gf_index)
                        break
                    gf_index += 1
                if not af.gfs:
                    instance.transfer_list.pop(af_index)
                    break
                af_index += 1

        return instance

    def delete_right(self, instance, right_name, right_type):
        print("in delete right")
        if right_type == "AF":
            index = 0
            for af in instance.delete_list:
                if af.af_name == right_name:
                    instance.direct_connect_afs_id.remove(af.model_af_pk)
                    instance.delete_list.pop(index)
                    break
                index += 1
        if right_type == "GF":
            index = 0
            af_index = 0
            for af in instance.delete_list:
                for gf in af.gfs:
                    if gf.gf_name == right_name:
                        af.gfs.pop(index)
                        break
                    index += 1
                if not af.gfs:
                    instance.delete_list.pop(af_index)
                    break
                af_index += 1
        if right_type == "TF":
            index = 0
            af_index = 0
            gf_index = 0
            for af in instance.delete_list:
                for gf in af.gfs:
                    for tf in gf.tfs:
                        if tf.tf_name == right_name:
                            gf.tfs.pop(index)
                            break
                        index += 1
                    if not gf.tfs:
                        af.gfs.pop(gf_index)
                        break
                    gf_index += 1
                if not af.gfs:
                    instance.delete_list.pop(af_index)
                    break
                af_index += 1

        return instance

    def clear_transferlist_and_deletelist(self, instance):
        print("in clear transfer- and deletelist")
        instance.transfer_list.clear()
        instance.delete_list.clear()
        return instance

    def remove_from_my_requests(self, instance, data):
        print("in remove_from_my_requests")
        instance.my_requests_id.remove(int(data['request_pk']))
        return instance

    def add_to_my_requests(self, instance, data):
        print("in add_to_my_requests")
        keys = json.loads(data['request_pks'])
        for key in keys:
            instance.my_requests_id.add(key)
        return instance

    def copy_user_right(self, right, type):
        if type == "af":
            u_af = User_AF(af_name=right.af_name, model_af_pk=int(float(right.model_af_pk)), gfs=[])
            # u_af.Meta.abstract = True
            for gf in right.gfs:
                u_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=int(float(gf.model_gf_pk)), tfs=[])
                # u_gf.Meta.abstract = True
                for tf in gf.tfs:
                    u_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.model_tf_pk)), color=tf.color)
                    # u_tf.Meta.abstract = True
                    u_gf.tfs.append(u_tf)
                u_af.gfs.append(u_gf)
            return u_af
        elif type == "gf":
            u_gf = User_GF(gf_name=right.gf_name, model_gf_pk=int(float(right.model_gf_pk)), tfs=[])
            for tf in right.tfs:
                u_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.model_tf_pk)), color=tf.color)
                u_gf.tfs.append(u_tf)
            return u_gf
        elif type == "tf":
            u_tf = User_TF(tf_name=right.tf_name, model_tf_pk=int(float(right.model_tf_pk)), color=right.color)
            return u_tf

    def add_to_transfer_list(self, instance, data):
        print("in add_to_transfer_lst")
        compareUser = User.objects.get(identity=data['compare_user'])
        if data['right_type'] == "af":
            for af in compareUser.user_afs:
                if af.af_name == data['right_name']:
                    cpy_af = self.copy_user_right(af, data['right_type'])
                    cpy_af.transfer = True
                    instance.transfer_list.append(cpy_af)
                    break
        # TODO: ab hier noch nicht durchgetestet
        elif data['right_type'] == "gf":
            for af in compareUser.user_afs:
                if af.af_name == data['parent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['right_name']:
                            added = False
                            cpy_gf = self.copy_user_right(gf, data['right_type'])
                            cpy_gf.transfer = True
                            for ele in instance.transfer_list:
                                if ele.af_name == data['parent']:
                                    ele.gfs.append(cpy_gf)
                                    added = True
                                    break
                            if not added:
                                cpy_af = User_AF(af_name=af.af_name, model_af_pk=af.model_af_pk, gfs=[])
                                cpy_af.gfs.append(cpy_gf)
                                instance.transfer_list.append(cpy_af)
                            break
                    else:
                        continue
                    break
        elif data['right_type'] == "tf":
            for af in compareUser.user_afs:
                if af.af_name == data['grandparent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['parent']:
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    cpy_tf = self.copy_user_right(tf, data['right_type'])
                                    cpy_tf.transfer = True
                                    added = False
                                    for ele in instance.transfer_list:
                                        if ele.af_name == data['grandparent']:
                                            for user_gf in ele.gfs:
                                                if user_gf.gf_name == data['parent']:
                                                    user_gf.tfs.append(cpy_tf)
                                                    added = True
                                                    break
                                            else:
                                                continue
                                            break
                                    if not added:
                                        cpy_af = User_AF(af_name=af.af_name, model_af_pk=af.model_af_pk, gfs=[])
                                        cpy_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.model_gf_pk, tfs=[])
                                        cpy_gf.tfs.append(cpy_tf)
                                        cpy_af.gfs.append(cpy_gf)
                                        instance.transfer_list.append(cpy_af)
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
        return instance

    def remove_from_transfer_list(self, instance, data):
        print("in remove from transfer_list")
        if data['right_type'] == "af":
            index = 0
            for right in instance.transfer_list:
                if right.af_name == data['right_name']:
                    instance.transfer_list.pop(index)
                    break
                index += 1
        elif data['right_type'] == "gf":
            af_index = 0
            for right in instance.transfer_list:
                if right.af_name == data['parent']:
                    index = 0
                    for gf in right.gfs:
                        if gf.gf_name == data['right_name']:
                            right.gfs.pop(index)
                            break
                        index += 1
                    if not right.gfs:
                        instance.transfer_list.pop(af_index)
                af_index += 1
        elif data['right_type'] == "tf":
            af_index = 0
            for right in instance.transfer_list:
                if right.af_name == data['grandparent']:
                    gf_index = 0
                    for gf in right.gfs:
                        if gf.gf_name == data['parent']:
                            index = 0
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    gf.tfs.pop(index)
                                    break
                                index += 1
                            if not gf.tfs:
                                right.gfs.pop(gf_index)
                                break
                        gf_index+=1
                    if not right.gfs:
                        instance.transfer_list.pop(af_index)
                        break
                af_index += 1

        return instance

    def remove_from_delete_list(self, instance, data):
        r_af = None
        index = 0
        for restore_af in instance.delete_list:
            if restore_af.af_name == data['right_name']:
                r_af = restore_af
                break
            index += 1

        af_found = False
        for af in instance.user_afs:
            if af.af_name == r_af.af_name:
                af_found = True
                break
        if af_found:
            for r_gf in r_af.gfs:
                gf_found = False
                for gf in af.gfs:
                    if gf.gf_name == r_gf.gf_name:
                        gf_found = True
                        break
                if gf_found:
                    for r_tf in r_gf.tfs:
                        tf_found = False
                        for tf in gf.tfs:
                            if tf.tf_name == r_tf.tf_name:
                                tf_found = True
                        if not tf_found:
                            r_tf.delete = False
                            gf.tfs.append(r_tf)
                else:
                    r_gf.delete = False
                    af.gfs.append(r_gf)
        else:
            r_af.delete = False
            instance.user_afs.append(r_af)

        instance.delete_list.pop(index)
        return instance

    def add_to_delete_list(self, instance, data):
        if data['right_type'] == 'af':
            index = 0
            for af in instance.user_afs:
                if af.af_name == data['right_name']:
                    af.delete = True
                    found = False
                    for del_af in instance.delete_list:
                        if del_af.af_name == data['right_name']:
                            found = True
                            break
                    if not found:
                        instance.delete_list.append(af)
                        instance.user_afs.pop(index)
                        return instance
                    else:
                        for gf in af.gfs:
                            del_af.gfs.append(gf)
                        instance.user_afs.pop(index)
                index += 1

        if data['right_type'] == 'gf':
            af_index = 0
            for af in instance.user_afs:
                if af.af_name == data['parent']:
                    index = 0
                    for gf in af.gfs:
                        if gf.gf_name == data['right_name']:
                            found = False
                            gf.delete = True
                            for del_af in instance.delete_list:
                                if del_af.af_name == data['parent']:
                                    found = True
                                    break
                            if not found:
                                cpy_af = User_AF(af_name=af.af_name, model_af_pk=af.model_af_pk,
                                                 af_applied=af.af_applied,
                                                 af_valid_from=af.af_valid_from, af_valid_till=af.af_valid_till, gfs=[])
                                cpy_af.gfs.append(gf)
                                instance.delete_list.append(cpy_af)
                            else:
                                for del_af in instance.delete_list:
                                    if del_af.af_name == data['parent']:
                                        del_af.gfs.append(gf)
                            af.gfs.pop(index)
                            if not af.gfs:
                                instance.user_afs.pop(af_index)
                            return instance
                        index += 1
                af_index += 1

        if data['right_type'] == 'tf':
            af_index = 0
            for af in instance.user_afs:
                if af.af_name == data['grandparent']:
                    gf_index = 0
                    for gf in af.gfs:
                        if gf.gf_name == data['parent']:
                            index = 0
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    tf.delete = True
                                    found = False
                                    for del_af in instance.delete_list:
                                        if del_af.af_name == data['grandparent']:
                                            found = True
                                            break
                                    if not found:
                                        cpy_af = User_AF(af_name=af.af_name, model_af_pk=af.model_af_pk,
                                                         af_applied=af.af_applied,
                                                         af_valid_from=af.af_valid_from, af_valid_till=af.af_valid_till,
                                                         gfs=[])
                                        cpy_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.model_gf_pk, tfs=[])
                                        cpy_af.gfs.append(cpy_gf)
                                        cpy_gf.tfs.append(tf)
                                        instance.delete_list.append(cpy_af)
                                        gf.tfs.pop(index)
                                        if not gf.tfs:
                                            af.gfs.pop(gf_index)
                                            if not af.gfs:
                                                instance.user_afs.pop(af_index)
                                        return instance
                                    else:
                                        gf_found = False
                                        for del_gf in del_af.gfs:
                                            if del_gf.gf_name == data['parent']:
                                                gf_found = True
                                                break
                                        if gf_found:
                                            del_gf.tfs.append(tf)
                                            gf.tfs.pop(index)
                                            if not gf.tfs:
                                                af.gfs.pop(gf_index)
                                                if not af.gfs:
                                                    instance.user_afs.pop(af_index)
                                            return instance
                                        else:
                                            cpy_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.model_gf_pk, tfs=[])
                                            cpy_gf.tfs.append(tf)
                                            del_af.gfs.append(cpy_gf)
                                            gf.tfs.pop(index)
                                            if not gf.tfs:
                                                af.gfs.pop(gf_index)
                                                if not af.gfs:
                                                    instance.user_afs.pop(af_index)
                                            return instance
                                index += 1
                        gf_index += 1
                af_index += 1

        return instance


class TFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = TF
        fields = ('pk','tf_name', 'tf_description','tf_application')

    pk = serializers.IntegerField()
    tf_name = serializers.CharField(max_length=150)
    tf_description = serializers.CharField(max_length=250)
    tf_application = TF_ApplicationSerializer()


class GFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = GF
        fields = ('pk','gf_name', 'gf_description', 'tfs')

    pk = serializers.IntegerField()
    gf_name = serializers.CharField(max_length=150)
    gf_description = serializers.CharField(max_length=250)
    tfs = TFModelRightsSerializer(many=True, read_only=True)


class AFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = AF
        fields = ('pk','af_name', 'af_description', 'gfs')

    pk = serializers.IntegerField()
    af_name = serializers.CharField(max_length=150)
    af_description = serializers.CharField(max_length=250)
    gfs = GFModelRightsSerializer(many=True, read_only=True)


class UserModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('url', 'pk', 'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs',)

    roles = UserSerializer(many=True, read_only=True)
    direct_connect_afs = AFModelRightsSerializer(many=True, read_only=True)
    direct_connect_gfs = GFSerializer(many=True, read_only=True)
    direct_connect_tfs = TFSerializer(many=True, read_only=True)


class UserListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'pk', 'identity', 'name', 'first_name', 'deleted',)
        lookup_field = 'identity'
        extra_kwargs = {
            'url': {'lookup_field': 'identity'}
        }


class CompleteUserListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'pk', 'identity', 'name', 'first_name', 'deleted', 'user_afs')
        lookup_field = 'identity'
        extra_kwargs = {
            'url': {'lookup_field': 'identity'}
        }

    user_afs = UserAFSerializer(many=True, read_only=True)

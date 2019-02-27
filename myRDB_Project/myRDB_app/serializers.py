from rest_framework import serializers
import copy
from .models import Orga, Department, Group, ZI_Organisation, TF_Application, TF, GF, AF, Role, User, User_GF, User_AF, \
    User_TF


class OrgaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Orga
        fields = ('url','pk', 'team', 'theme_owner')


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department
        fields = ('url','pk', 'department_name')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url','pk', 'group_name')


class ZI_OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ZI_Organisation
        fields = ('url','pk', 'zi_organisation_name')


class TF_ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF_Application
        fields = ('url','pk', 'application_name','color')


class TFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF
        fields = ('url','pk', 'tf_name', 'tf_description', 'tf_owner_orga', 'tf_application', 'criticality',
                  'highest_criticality_in_AF')
    tf_owner_orga = OrgaSerializer()
    tf_application = TF_ApplicationSerializer()
class GFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GF
        fields = ('url','pk', 'gf_name', 'gf_description', 'tfs')
    tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='tf-detail')

class AFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AF
        fields = ('url','pk', 'af_name', 'af_description', 'af_applied', 'af_valid_from', 'af_valid_till', 'gfs')
    gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='gf-detail')

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('url','pk', 'role_name', 'role_description', 'afs')
    afs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='role-detail')

class UserTFSerializer(serializers.Serializer):
    tf_name = serializers.CharField(max_length=150)
    model_tf_pk = serializers.IntegerField()
    on_delete_list = serializers.BooleanField(default=False)
    color = serializers.CharField(default="hsl(0, 100, 100)", max_length=25)

class UserGFSerializer(serializers.Serializer):
    gf_name = serializers.CharField(max_length=150)
    model_gf_pk = serializers.IntegerField()
    on_delete_list = serializers.BooleanField(default=False)
    tfs = UserTFSerializer(many=True, read_only=False)

class UserAFSerializer(serializers.Serializer):
    af_name = serializers.CharField(max_length=150)
    model_af_pk = serializers.IntegerField()
    on_delete_list = serializers.BooleanField(default=False)
    gfs = UserGFSerializer(many=True, read_only=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
        'url','pk', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
        'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password','user_afs','transfer_list')

    roles = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='role-detail')
    direct_connect_afs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='af-detail')
    direct_connect_gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='gf-detail')
    direct_connect_tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='tf-detail')
    user_afs = UserAFSerializer(many=True, read_only=True)
    transfer_list = UserAFSerializer(many=True, read_only=False)

    orga = OrgaSerializer()
    department = DepartmentSerializer()
    group = GroupSerializer()
    zi_organisation = ZI_OrganisationSerializer()

    def update(self, instance, validated_data):
        print("im in the serializer-update-method")
        print(self._kwargs)
        data=self._kwargs['data']
        if data['action_type'] == 'trash':
            instance = self.set_on_delete_list(instance,data,True)
        elif data['action_type']=="restore":
            instance = self.set_on_delete_list(instance,data,False)
        elif data['action_type']=="transfer":
            instance = self.add_to_transfer_list(instance, data)
        elif data['action_type']=="restore_transfer":
            instance = self.remove_from_transfer_list(instance, data)
        instance.save()

        return instance

    def copy_user_right(self, right, type):
        if type == "af":
            u_af = User_AF(af_name=right.af_name, model_af_pk=int(float(right.model_af_pk)), gfs=[])
            #u_af.Meta.abstract = True
            for gf in right.gfs:
                u_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=int(float(gf.model_gf_pk)), tfs=[])
                #u_gf.Meta.abstract = True
                for tf in gf.tfs:
                    u_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=int(float(tf.model_tf_pk)), color=tf.color)
                    #u_tf.Meta.abstract = True
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


    def add_to_transfer_list(self,instance, data):

        print("in add_to_transfer_lst")
        compareUser = User.objects.get(identity=data['compare_user'])
        if data['right_type']=="af":
            for af in compareUser.user_afs:
                if af.af_name == data['right_name']:
                    cpy_af = self.copy_user_right(af,data['right_type'])
                    instance.transfer_list.append(cpy_af)
                    break
        # TODO: ab hier noch nicht durchgetestet
        elif data['right_type']=="gf":
            for af in compareUser.user_afs:
                if af.af_name == data['parent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['right_name']:
                            added = False
                            cpy_gf = self.copy_user_right(gf,data['right_type'])
                            for ele in instance.transfer_list:
                                if ele.af_name == data['parent']:
                                    ele.gfs.append(cpy_gf)
                                    added = True
                                    break
                            else:
                                continue
                            if not added:
                                cpy_af = User_AF(af_name=af.af_name,model_af_pk=af.model_af_pk,gfs=[])
                                cpy_af.gfs.append(cpy_gf)
                                instance.transfer_list.append(cpy_af)
                            break
                    else:
                        continue
                    break
        elif data['right_type']=="tf":
            for af in compareUser.user_afs:
                if af.af_name == data['grandparent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['parent']:
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    cpy_tf = self.copy_user_right(tf, data['right_type'])
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
                                    else:
                                        continue
                                    if not added:
                                        cpy_af = User_AF(af_name=af.af_name, model_af_pk=af.model_af_pk, gfs=[])
                                        cpy_gf = User_GF(gf_name=gf.gf_name,model_gf_pk=gf.mode_gf_pk,tfs=[])
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
            for right in instance.transfer_list:
                if right.af_name == data['parent']:
                    index = 0
                    for gf in right.gfs:
                        if gf.gf_name == data['right_name']:
                            right.gfs.pop(index)
                            break
                        index += 1
                    else:
                        continue
                    break
        elif data['right_type'] == "tf":
            for right in instance.transfer_list:
                if right.af_name == data['grandparent']:
                    for gf in right.gfs:
                        if gf.gf_name == data['parent']:
                            index = 0
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    # TODO: immer fehler beim versuch einzelne TF zu löschen -> meta.pk Nonetype dosent hav attr attaname
                                    gf.tfs.pop(index)
                                    break
                                index += 1
                            else:
                                continue
                            break
                    else:
                        continue
                    break


        return instance

    def set_on_delete_list(self,instance,data,bool):
        if data['right_type'] == 'af':
            for af in instance.user_afs:
                if af.af_name == data['right_name']:
                    af.on_delete_list = bool
                    for gf in af.gfs:
                        gf.on_delete_list = bool
                        for tf in gf.tfs:
                            tf.on_delete_list = bool
                    break
        if data['right_type'] == 'gf':
            for af in instance.user_afs:
                if af.af_name==data['parent']:
                    for gf in af.gfs:
                        if gf.gf_name == data['right_name']:
                            gf.on_delete_list = bool
                            for tf in gf.tfs:
                                tf.on_delete_list = bool
                            break
                    else:
                        continue
                    break
        if data['right_type'] == 'tf':
            for af in instance.user_afs:
                if af.af_name==data['grandparent']:
                    for gf in af.gfs:
                        if gf.gf_name==data['parent']:
                            for tf in gf.tfs:
                                if tf.tf_name == data['right_name']:
                                    tf.on_delete_list = bool
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
        return instance



class TFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = TF
        fields = ('tf_name','tf_description')
    tf_name = serializers.CharField(max_length=150)
    tf_description = serializers.CharField(max_length=250)

class  GFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = GF
        fields = ('gf_name','gf_description','tfs')
    gf_name = serializers.CharField(max_length=150)
    gf_description = serializers.CharField(max_length=250)
    tfs = TFModelRightsSerializer(many= True, read_only=True)

class AFModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = AF
        fields = ('af_name','af_description','gfs')
    af_name = serializers.CharField(max_length=150)
    af_description = serializers.CharField(max_length=250)
    gfs = GFModelRightsSerializer(many= True, read_only=True)

class UserModelRightsSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('url','pk','roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs',)
    roles = UserSerializer(many=True, read_only=True)
    direct_connect_afs = AFModelRightsSerializer(many=True, read_only=True)
    direct_connect_gfs = GFSerializer(many=True, read_only=True)
    direct_connect_tfs = TFSerializer(many=True, read_only=True)


class UserListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'pk','identity', 'name', 'first_name', 'deleted', )

class CompleteUserListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url','pk', 'identity', 'name', 'first_name', 'deleted','user_afs' )

    user_afs = UserAFSerializer(many=True, read_only=True)




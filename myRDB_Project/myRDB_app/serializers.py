from rest_framework import serializers
from .models import Orga, Department, Group, ZI_Organisation, TF_Application, TF, GF, AF, Role, User


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
        fields = ('url','pk', 'application_name')


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

class UserGFSerializer(serializers.Serializer):
    gf_name = serializers.CharField(max_length=150)
    model_gf_pk = serializers.IntegerField()
    on_delete_list = serializers.BooleanField(default=False)
    tfs = UserTFSerializer(many=True, read_only=True)

class UserAFSerializer(serializers.Serializer):
    af_name = serializers.CharField(max_length=150)
    model_af_pk = serializers.IntegerField()
    on_delete_list = serializers.BooleanField(default=False)
    gfs = UserGFSerializer(many=True, read_only=True)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
        'url','pk', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
        'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password','user_afs')

    roles = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='role-detail')
    direct_connect_afs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='af-detail')
    direct_connect_gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='gf-detail')
    direct_connect_tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='tf-detail')
    user_afs = UserAFSerializer(many=True, read_only=True)

    orga = OrgaSerializer()
    department = DepartmentSerializer()
    group = GroupSerializer()
    zi_organisation = ZI_OrganisationSerializer()

    def update(self, instance, validated_data):
        print("im in the serializer-update-method")
        print(self._kwargs)
        data=self._kwargs['data']
        if data['right_type'] == 'af':
            for af in instance.user_afs:
                if af.af_name == data['right_name']:
                    af.on_delete_list = True
                    break
        if data['right_type'] == 'gf':
            for af in instance.user_afs:
                for gf in af.gfs:
                    if gf.gf_name == data['right_name']:
                        gf.on_delete_list = True
                        break
                else:
                    continue
                break
        if data['right_type'] == 'tf':
            for af in instance.user_afs:
                for gf in af.gfs:
                    for tf in gf.tfs:
                        if tf.tf_name == data['right_name']:
                            tf.on_delete_list = True
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break

        instance.save()

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




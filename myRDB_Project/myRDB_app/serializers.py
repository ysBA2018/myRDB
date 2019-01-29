from rest_framework import serializers
from .models import Orga, Department, Group, ZI_Organisation, TF_Application, TF, GF, AF, Role, User


class OrgaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Orga
        fields = ('url', 'team', 'theme_owner')


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department
        fields = ('url', 'department_name')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'group_name')


class ZI_OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ZI_Organisation
        fields = ('url', 'zi_organisation_name')


class TF_ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF_Application
        fields = ('url', 'application_name')


class TFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TF
        fields = ('url', 'tf_name', 'tf_description', 'tf_owner_orga', 'tf_application', 'criticality',
                  'highest_criticality_in_AF')
    tf_owner_orga = OrgaSerializer()
    tf_application = TF_ApplicationSerializer()
class GFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GF
        fields = ('url', 'gf_name', 'gf_description', 'tfs')
    tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='tf-detail')

class AFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AF
        fields = ('url', 'af_name', 'af_description', 'af_applied', 'af_valid_from', 'af_valid_till', 'gfs')
    gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='gf-detail')

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('url', 'role_name', 'role_description', 'afs')
    afs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='role-detail')

class UserTFSerializer(serializers.Serializer):
    tf_name = serializers.CharField(max_length=150)
    model_tf_pk = serializers.IntegerField()

class UserGFSerializer(serializers.Serializer):
    gf_name = serializers.CharField(max_length=150)
    model_gf_pk = serializers.IntegerField()
    tfs = UserTFSerializer(many=True, read_only=True)

class UserAFSerializer(serializers.Serializer):
    af_name = serializers.CharField(max_length=150)
    model_af_pk = serializers.IntegerField()
    gfs = UserGFSerializer(many=True, read_only=True)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
        'url', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
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





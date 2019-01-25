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

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
        'url', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
        'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password')

    roles = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='role-detail')
    direct_connect_afs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='af-detail')
    direct_connect_gfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='gf-detail')
    direct_connect_tfs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='tf-detail')

    orga = OrgaSerializer()
    department = DepartmentSerializer()
    group = GroupSerializer()
    zi_organisation = ZI_OrganisationSerializer()


class ProfileGFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GF
        fields = ('url', 'gf_name', 'gf_description', 'tfs')
    tfs = TFSerializer(many=True, read_only=True)


class ProfileAFSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AF
        fields = ('url', 'af_name', 'af_description', 'af_applied', 'af_valid_from', 'af_valid_till', 'gfs')
    gfs = ProfileGFSerializer(many=True, read_only=True)


class ProfileRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('url', 'role_name', 'role_description', 'afs')
    afs = ProfileAFSerializer(many=True, read_only=True)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
        'url', 'identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group', 'zi_organisation',
        'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff', 'password')

    roles = ProfileRoleSerializer(many=True, read_only=True)
    direct_connect_afs = ProfileAFSerializer(many=True, read_only=True)
    direct_connect_gfs = ProfileGFSerializer(many=True, read_only=True)
    direct_connect_tfs = TFSerializer(many=True, read_only=True)

    orga = OrgaSerializer()
    department = DepartmentSerializer()
    group = GroupSerializer()
    zi_organisation = ZI_OrganisationSerializer()




from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, UsernameField
from django.utils.safestring import mark_safe

from django.contrib.auth import get_user_model

from .models import User, Orga, Group, Department, ZI_Organisation, Role, AF, GF, TF, User_AF, User_GF, User_TF, \
    ChangeRequests


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ('identity',)



class CustomUserCreationForm(UserCreationForm):
    '''
        Form for password and xvNumber validation
        also checks if Profile has already been activated by any user by creating pswd
            otherwise create new
    '''
    class Meta:
        model = get_user_model()
        fields = ('identity','email')

    # Validation von xvnummer abgeschaltet da dieses bei passwortvalidierung mit dabei
    '''
    def clean_identity(self):
        print("in clean identity")
        identity = self.cleaned_data.get("identity")
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(identity=identity)
            self.errors['identity'] = self.error_class()
            print("user exists")

        except User.DoesNotExist:
            print("in does not exist")
            pass
        return identity
    '''

    def clean(self):
        print("in clean_password2")
        cd = self.cleaned_data
        password1 = cd.get("password1")
        password2 = cd.get("password2")
        if password1 and password2 and password1 != password2:
            print("in passwords dont match")

            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return cd

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        identity = self.cleaned_data['identity']
        identity_upper = identity.upper()
        print("in save!")
        print(identity, identity_upper)
        try:
            user = User.objects.get(identity=identity)
            print("User: ", user.__str__(), " mit Identity_lower existiert")
            if user.password == "":
                print("User mit Identity_lower existiert - password is leer -> pw wird gesafet")
                user.set_password(self.cleaned_data['password1'])
                user.save()
            else:
                print("User mit Identity_lower existiert und hat pw!")
                forms.ValidationError("User mit Identity_lower existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
        except(KeyError, User.DoesNotExist):
            try:
                user = User.objects.get(identity=identity_upper)
                print("User: ", user.__str__(), " mit Identity_upper existiert")
                if user.password == "":
                    print("User mit Identity_upper existiert - password is leer -> pw wird gesafet")
                    user.set_password(self.cleaned_data['password1'])
                    user.save()
                else:
                    forms.ValidationError("User mit Identity_upper existiert und hat pw!")
                    print("User mit Identity_upper existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
            except(KeyError, User.DoesNotExist):
                print("User existiert nicht - wird neu angelegt")
                user = super(CustomUserCreationForm, self).save(commit=False)
                user.set_password(self.cleaned_data['password1'])
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
                if commit:
                    user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('identity',)
        error_css_class = 'error'


class SomeForm(forms.Form):
    start_import = forms.FileInput()


class ApplyRightForm(forms.Form):
    reason_for_application = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}), min_length=20, max_length=500,
                                             label=mark_safe('<strong>Grund der Beantragung:</strong>'))


class DeleteRightForm(forms.Form):
    reason_for_deletion = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}), min_length=20, max_length=500,
                                          label=mark_safe('<strong>Grund der Löschung:</strong>'))


class AcceptChangeForm(forms.Form):
    change_in_IIQ_check = forms.BooleanField(label="Änderungen in IIQ beantragt?")


class DeclineChangeForm(forms.Form):
    reason_for_decline = forms.CharField(widget=forms.Textarea(attrs={'rows': '2'}), min_length=20, max_length=500,
                                         label=mark_safe('<strong>Grund der Ablehnung:</strong>'))

class ProfileHeaderForm(forms.Form):
    user_search = forms.CharField(label="",widget=forms.TextInput(attrs={'placeholder': 'vergleiche mit...'}))

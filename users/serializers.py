from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from users import users_constants
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email, user_field
from allauth.utils import get_user_model
from allauth.account.models import EmailAddress

class GeneralAccountSerializer(serializers.ModelSerializer):
    """
    Сериализатор аккаунта.
    """

    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        exclude = [
            'created_by', 'modified_by', 'user_permissions', 'groups', 'is_superuser', 'is_active', 'password'
        ]
        read_only_fields = [
            'id', 'date_joined', 'updated_at', 'account_type', 'last_login'
        ]


class UserInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор аккаунта.
    """


    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'email',
            'date_joined', 'contacts_info', 'avatar', 'additional_info', 'skills'
        ]
        read_only_fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'email', 'additional_info',
            'date_joined', 'contacts_info', 'avatar'
        ]

class PublicUserInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор аккаунта.
    """


    class Meta:
        """
        Настройки сериализатора.
        """
        model = get_user_model()
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'email',
            'date_joined', 'avatar', 'additional_info', 'skills'
        ]
        read_only_fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'email', 'additional_info',
            'date_joined', 'avatar'
        ]


class OauthParamsSerializer(serializers.Serializer):
    """
    Сериализатор параметров провайдера авторизации.
    """

    client_id = serializers.CharField(help_text='Идентификатор пользователя провайдера', min_length=1, max_length=200)
    state = serializers.CharField(help_text='Идентификатор состояния авторизации', min_length=1, max_length=200)


class KnoxSerializer(serializers.Serializer):
    """
    Serializer for Knox authentication.
    """
    token = serializers.CharField()
    user = UserDetailsSerializer()


class KnoxRegisterSerializer(serializers.Serializer):
    """Сериализатор для параметров регистрации пользователя"""

    username = serializers.CharField(max_length=32, min_length=4, required= True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    account_type = serializers.ChoiceField(allow_blank = True, choices=users_constants.USERS_TYPES)
    default_error_messages = {
    'email_taken': '__ALREADY_REGISTERED__',
    'email_not_confirmed':'__EMAIL_NOT_CONFIRMED__'
}

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'account_type': self.validated_data.get('account_type', '')
        }


    def validate_username(self, username):

        username = get_adapter().clean_username(username)

        return username


    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        user = EmailAddress.objects.filter(email__iexact = email)
        if user:
            if user[0].verified == True:
                self.fail('email_taken')
            else:
                self.fail('email_not_confirmed')
        else:
            return email


    def validate_password1(self, password):

        return get_adapter().clean_password(password)


    def validate(self, data):

        if data['password1'] != data['password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data


    def save(self, request):

        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        self.save_user(request, user)
        setup_user_email(request, user, [])
        return user


    def save_user(self, request, user,):

        data = self.cleaned_data
        email = data.get("email")
        username = data.get("username")
        account_type = data.get('account_type')
        user_field(user, 'email', email)
        user_field(user, 'username', username)
        if account_type:
            user_field(user, "account_type", account_type)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        user.save()
        return user

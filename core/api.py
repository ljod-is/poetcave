from core.models import User
from django.contrib.auth import login as user_login
from django.core.exceptions import PermissionDenied
from ninja import NinjaAPI
from ninja import Schema

api = NinjaAPI()


class LoginRequestSchema(Schema):
    email: str
    password: str


class UserSchema(Schema):
    email: str
    contact_name: str
    contact_address: str
    contact_postal_code: str
    contact_place: str
    contact_phone: str


@api.post("login/", response=UserSchema)
def login(request, input: LoginRequestSchema):
    try:
        user = User.objects.get(email=input.email)
        if user.check_password(input.password):
            user_login(request, user)
            return {
                "email": user.email,
                "contact_name": user.contact_name,
                "contact_address": user.contact_address,
                "contact_postal_code": user.contact_postal_code,
                "contact_place": user.contact_place,
                "contact_phone": user.contact_phone,
            }

        raise PermissionDenied
    except User.DoesNotExist:
        raise PermissionDenied

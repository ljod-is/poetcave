from core.models import User
from django.contrib.auth import login as user_login
from ninja import Router
from ninja import Schema

router = Router()


def permission_denied_response(error_message: str = "Unauthorized"):
    return 401, {
        "error_message": error_message,
    }


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


class ErrorSchema(Schema):
    error_message: str


@router.post("login/", response={200: UserSchema, 401: ErrorSchema})
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

        return permission_denied_response("Login failed")
    except User.DoesNotExist:
        return permission_denied_response("Login failed")

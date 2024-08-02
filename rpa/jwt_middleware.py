from django.http import JsonResponse
import jwt
from django.conf import settings
from django.shortcuts import redirect
from rpa.models import Users, AdminUsers
import hashlib



class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # return self.get_response(request)
        print(request.path)

        jwt_token = request.session.get("jwt_token")
        email = request.session.get("email")


        
        if request.path in settings.JWT_MIDDLEWARE_EXCLUDED_PATHS:
            return self.get_response(request)

        elif request.path.startswith(settings.JWT_MIDDLEWARE_USER_PATH):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_user(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")
        
        elif request.path.startswith(settings.JWT_MIDDLEWARE_ADMIN_PATH):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_admin(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")
        
        elif request.path.startswith(settings.JWT_MIDDLEWARE_STATIC_PATH + "upload/") and not request.path.endswith("/admin"):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_user(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")
        
        elif request.path.startswith(settings.JWT_MIDDLEWARE_STATIC_PATH + "upload/") and request.path.endswith("/admin"):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_admin(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")
        
        elif request.path.startswith(settings.JWT_MIDDLEWARE_STATIC_PATH + "word/") and request.path.endswith("/user"):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_user(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")
        
        elif request.path.startswith(settings.JWT_MIDDLEWARE_STATIC_PATH + "word/") and request.path.endswith("/admin"):
            if jwt_token and email:
                try:
                    decoded_jwt = jwt.decode(
                    jwt_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                except (jwt.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
                    request.session["FACULTY_NAME"] = None
                    request.session["email"] = None
                    request.session["jwt_token"] = None
                    return redirect("/rpa/login/")

                if not check_jwt_admin(decoded_jwt, email):
                    return redirect("/rpa/login/")

                response = self.get_response(request)
                return response
            else:
                return redirect("/rpa/login/")


def check_jwt_user(decoded_jwt, email):
    user = decoded_jwt['user']

    if not decoded_jwt['is_user']:
        return False
    
    user_record = Users.objects.get(email_id = email)

    if not user_record:
        return False
    
    email_db = user_record.email_id

    encoded_email_db = hashlib.sha256(email_db.encode("UTF-8")).hexdigest()

    if encoded_email_db != user:
        return False
    
    return True
    

def check_jwt_admin(decoded_jwt, email):
    user = decoded_jwt['user']

    if not decoded_jwt['is_admin']:
        return False
    
    admin_record = AdminUsers.objects.get(email_id = email)

    if not admin_record:
        return False
    
    email_db = admin_record.email_id

    encoded_email_db = hashlib.sha256(email_db.encode("UTF-8")).hexdigest()

    if encoded_email_db != user:
        return False
    
    return True

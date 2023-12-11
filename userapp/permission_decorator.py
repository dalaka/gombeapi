from functools import wraps

import jwt
from django.contrib.auth.models import Group
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from GombeLine import settings
from userapp.models import User
def response_info(status,msg, data):
    res={"status": status, "message": msg, "data": data}
    return res

def _is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        #dpt=Department.objects.filter(name=group_name['grp'],user=user)
        dpt = user.department.all()
        rst=user.groups.all()
        if  dpt.exists():
            if dpt.filter(name=group_name['grp']).exists():
                for grp in group_name['perm']:
                    if rst.exists():
                        result=rst.filter(name=grp).exists()

                        #result = IRMPermission.objects.get(name=grp).user_set.filter(id=user.id).exists()

                        return result
                    else:
                        return False

    except Group.DoesNotExist:
        return None

def has_permission(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            oken = get_authorization_header(args[0].request).decode('utf-8')
            r = oken.replace('Bearer', '')
            res = jwt.decode(r.replace(' ', ''), settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=res['user_id'])
            if user.is_authenticated:
                res = any([_is_in_group(user, group_name) for group_name in perm_name])

                if res:
                    print("Calling Function: " + view_func.__name__)
                else:
                    raise PermissionDenied
            else:
                AuthenticationFailed(detail=res,code=403)
            return view_func(*args, **kwargs)
        return _wrapped_view
    return decorator


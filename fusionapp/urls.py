from django.urls import path
from .views import *

urlpatterns = [
     path('signup/', SignUpAPIView.as_view(), name='signup'),
     path('signin/', SignInAPIView.as_view(), name='signin'),
     path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
     path('invite-member/', InviteMemberAPIView.as_view(), name='invite-member'),
     path('delete-member/', DeleteMemberAPIView.as_view(), name='delete-member'),
     path('update-member-role/', UpdateMemberRoleAPIView.as_view(), name='update-member-role'),

     #API for Stats
    path('role-wise-users/', RoleWiseNumberOfUsersAPIView.as_view(), name='role-wise-users'),
    path('org-wise-members/', OrganizationWiseNumberOfMembersAPIView.as_view(), name='org-wise-members'),
    path('org-role-wise-users/', OrganizationWiseRoleWiseNumberOfUsersAPIView.as_view(), name='org-role-wise-users'),
]

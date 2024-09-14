from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from .serializers import *


class SignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully, and invite email sent!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Password reset successfully, and alert email sent!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InviteMemberAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InviteMemberSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            organization = serializer.validated_data['organization']
            role = serializer.validated_data['role']
            user, created = User.objects.get_or_create(email=email)

            # If user is created, set a default password and send invitation email
            if created:
                user.save()

                # Generate the invite link (for example, you can use a token system)
                invite_link = f"http://yourdomain.com/invite/{organization.id}/{user.id}/"

                # Send invitation email
                send_mail(
                    'Invitation to join organization',
                    f'You have been invited to join the organization "{organization.name}". '
                    f'Click the link below to accept the invitation:\n\n{invite_link}',
                    'perveenadeepakgmail.com',
                    [user.email],
                    fail_silently=False,
                )

            # Add the user to the organization with the specified role
            member = Member.objects.create(
                user=user,
                org_id=organization.id,
                role_id=role.id,
                status=1,  # Active status (or any default status)
            )

            return Response({
                'message': f'Invitation sent to {email}.'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    from rest_framework import serializers
from .models import Member

class DeleteMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    org_id = serializers.IntegerField()

    def validate(self, data):
        user_id = data.get('user_id')
        org_id = data.get('org_id')

        # Check if the member exists in the given organization
        if not Member.objects.filter(user_id=user_id, org_id=org_id).exists():
            raise serializers.ValidationError("This member is not part of the specified organization.")

        return data



class DeleteMemberAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DeleteMemberSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            org_id = serializer.validated_data['org_id']

            # Delete the member from the organization
            Member.objects.filter(user_id=user_id, org_id=org_id).delete()

            return Response({'message': 'Member deleted successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UpdateMemberRoleAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UpdateMemberRoleSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.validated_data['member']
            role = serializer.validated_data['role']

            # Update the member's role
            member.role_id = role.id
            member.save()

            return Response({'message': 'Member role updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API for Stats


class RoleWiseNumberOfUsersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        role_stats = Role.objects.annotate(user_count=Count('member__user')).values('name', 'user_count')
        return Response(role_stats, status=200)

class OrganizationWiseNumberOfMembersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        org_stats = Organization.objects.annotate(member_count=Count('member')).values('name', 'member_count')
        return Response(org_stats, status=200)

class OrganizationWiseRoleWiseNumberOfUsersAPIView(APIView):
    def get(self, request, *args, **kwargs):
        org_role_stats = (
            Organization.objects
            .annotate(
                role_stats=Count('member__user', distinct=True)
            )
            .values('name', 'role__name', 'role_stats')
        )
        return Response(org_role_stats, status=200)
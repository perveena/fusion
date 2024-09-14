from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import User, Organization, Member, Role
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    org_name = serializers.CharField()

    def create(self, validated_data):
        # Create the user entry
        email = validated_data['email']
        password = make_password(validated_data['password'])  # Hash the password
        user = User.objects.create(email=email, password=password)

        # Create the organization
        org_name = validated_data['org_name']
        organization = Organization.objects.create(name=org_name)

        # Create the owner role
        role = Role.objects.create(name="Owner", org=organization)

        # Add the user as a member of the organization with the owner role
        member = Member.objects.create(user=user, org=organization, role=role)

        # Generate an invite link (for simplicity, using a random token here)
        invite_token = get_random_string(length=32)  # Random token for invite
        invite_link = f"http://yourdomain.com/invite/{invite_token}"

        # Send an invite email
        send_mail(
            'Welcome to Your Organization',
            f"Hello {email},\n\nYou have been added as the owner of the organization '{org_name}'.\nClick here to get started: {invite_link}",
            'perveenadeepakgmail.com',  # Sender's email
            [email],  # Recipient's email
            fail_silently=False,
        )

        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        # If user is authenticated, generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Send login alert email
        send_mail(
            'Login Alert',
            f"Hello {user.email},\n\nA login was detected on your account. If this wasn't you, please reset your password immediately.",
            'perveenadeepakgmail.com',
            [user.email],
            fail_silently=False,
        )

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        new_password = data.get('new_password')

        try:
            # Check if the user exists
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

        # Update the password
        user.password = make_password(new_password)  # Hash the new password
        user.save()

        # Send password update alert email
        send_mail(
            'Password Updated Successfully',
            f"Hello {user.email},\n\nYour password has been successfully updated. If this wasn't you, please contact support immediately.",
            'perveenadeepakgmail.com',
            [user.email],
            fail_silently=False,
        )

        return data



class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    org_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, data):
        email = data.get('email')
        org_id = data.get('org_id')
        role_id = data.get('role_id')

        # Check if the organization exists
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Organization not found.")

        # Check if the role exists
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found.")

        # Check if the user exists, if not, create a new user
        user, created = User.objects.get_or_create(email=email)

        # If the user already exists, check if they're already a member of the organization
        if not created:
            if Member.objects.filter(user=user, org_id=org_id).exists():
                raise serializers.ValidationError("User is already a member of this organization.")

        # Save organization and role in validated data for use in the view
        data['organization'] = organization
        data['role'] = role
        return data


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


class UpdateMemberRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    org_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, data):
        user_id = data.get('user_id')
        org_id = data.get('org_id')
        role_id = data.get('role_id')

        # Check if the member exists in the organization
        try:
            member = Member.objects.get(user_id=user_id, org_id=org_id)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found in the organization.")

        # Check if the role exists
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found.")

        # Save the member and role for use in the view
        data['member'] = member
        data['role'] = role
        return data

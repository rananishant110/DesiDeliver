from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import CustomUser





class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'business_name': user.business_name,
                    'business_type': user.business_type
                },
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'business_name': user.business_name,
                    'business_type': user.business_type,
                    'is_verified': user.is_verified,
                    'is_staff': user.is_staff
                },
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout_view(request):
    """User logout endpoint"""
    
    try:
        # For JWT, we just logout the user (tokens are stateless)
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update endpoint"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.UpdateAPIView):
    """Password change endpoint"""
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Generate new JWT tokens after password change
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Password changed successfully',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request_view(request):
    """Password reset request endpoint"""
    
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = CustomUser.objects.get(email=email)
        
        # TODO: Implement actual password reset email functionality
        # For now, just return success message
        
        return Response({
            'message': 'Password reset email sent successfully',
            'note': 'Check your email for password reset instructions'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm_view(request):
    """Password reset confirmation endpoint"""
    
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        # TODO: Implement actual password reset token validation
        # For now, just return success message
        
        return Response({
            'message': 'Password reset successful',
            'note': 'You can now login with your new password'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_view(request):
    """User dashboard endpoint"""
    
    user = request.user
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'business_name': user.business_name,
            'business_type': user.business_type,
            'is_verified': user.is_verified,
            'created_at': user.created_at
        },
        'business_info': user.get_business_info()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_business_view(request):
    """Business verification endpoint (admin only)"""
    
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        
        return Response({
            'message': f'Business {user.business_name} verified successfully'
        })
    
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

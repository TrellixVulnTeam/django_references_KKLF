import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .forms import UserCreationForm
from rest_framework import generics

from .models import PhoneToken, User
from .serializers import (
    PhoneTokenCreateSerializer, PhoneTokenValidateSerializer, UsersListSerializer
)
from .utils import user_detail
from rest_framework.permissions import IsAuthenticated


class GenerateOTP(CreateAPIView):
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenCreateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if ser.is_valid():
            token = PhoneToken.create_otp_for_number(
                request.data.get('phone_number')
            )
            if token:
                phone_token = self.serializer_class(
                    token, context={'request': request}
                )
                data = phone_token.data
                if getattr(settings, 'PHONE_LOGIN_DEBUG', False):
                    data['debug'] = token.otp
                return Response(data)
            return Response({
                'reason': "you can not have more than {n} attempts per day, please try again tomorrow".format(
                    n=getattr(settings, 'PHONE_LOGIN_ATTEMPTS', 10))}, status=status.HTTP_403_FORBIDDEN)
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ValidateOTP(CreateAPIView):
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenValidateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(
            data=request.data, context={'request': request}
        )
        if ser.is_valid():
            pk = request.data.get("pk")
            otp = request.data.get("otp")
            try:
                user = authenticate(request, pk=pk, otp=otp)
                if user:
                    last_login = user.last_login
                login(request, user)
                response = user_detail(user, last_login)
                return Response(response, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                    {'reason': "OTP doesn't exist"},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


@login_required
def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.POST.get('username')))[:6]
            created_user = form.save()
            created_user.private_code = user_code
            created_user.invite_code = form.cleaned_data.get('invite_code')
            created_user.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


class UsersListView(generics.ListCreateAPIView):
    # queryset = Case.objects.all()
    serializer_class = UsersListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(invite_code=self.request.user.private_code)

    def list(self, request):
        queryset = self.get_queryset()
        return Response({'users': queryset})



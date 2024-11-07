import json

import requests
from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from Game.models import AvatarOwnerShip, Avatar
from Shop.models import Package, ZarinpalCode, Transaction
from Shop.serializers import PackageSerializer, AddTransactionSerializer
from Users.models import CustomUser, Wallet

ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

CallbackURL = 'https://api.baclass.app/api/shop/package/verify/'


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_wallet(self):
        return get_object_or_404(Wallet, user=self.get_user())

    def get_queryset(self):
        return Package.objects.filter(is_available=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def zarinpal(self, request, *args, **kwargs):
        package = Package.objects.get(id=request.data['package'])

        serializer = AddTransactionSerializer(data={'user': request.user.id,
                                                    'package': package.id,
                                                    'price': package.price,
                                                    'gateway': 'zarinpal',
                                                    'gateway_code': ZarinpalCode.objects.last().code,
                                                    'description': 'خرید ' + package.name})
        if serializer.is_valid():
            transaction = serializer.save()
            return Response({
                'purchase_url': '?merchant=' + ZarinpalCode.objects.last().code
                                + "&phone=" + CustomUser.objects.get(id=request.user.id).phone
                                + "&amount=" + str(int(transaction.price))
                                + "&description=" + 'خرید اشتراک ' + package.name
                                + "&transaction_id=" + str(transaction.id)
            },
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @action(detail=False, permission_classes=[AllowAny])
    def pay(self, request, *args, **kwargs):
        req_data = {
            "merchant_id": request.GET['merchant'],
            "amount": int(request.GET['amount']),
            "callback_url": CallbackURL,
            "description": request.GET['description'],
            "metadata": {"phone": request.GET['phone'], "email": ''},
        }
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        authority = req.json()['data']['authority']

        transaction = Transaction.objects.get(id=request.GET['transaction_id'])
        transaction.gateway_code = authority
        transaction.save()

        if len(req.json()['errors']) == 0:
            return redirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")

    @action(detail=False, permission_classes=[AllowAny])
    def verify(self, request, *args, **kwargs):
        t_authority = request.GET['Authority']

        if request.GET.get('Status') == 'OK':

            transaction = Transaction.objects.get(gateway_code=t_authority)

            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req_data = {
                "merchant_id": ZarinpalCode.objects.last().code,
                "amount": transaction.price,
                "authority": t_authority
            }
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']

                if t_status == 100:
                    # save reservation
                    transaction.state = 'success'
                    transaction.tracking_code = req.json()['data']['ref_id']
                    transaction.save()

                    # update expire date
                    wallet = Wallet.objects.get(user=transaction.user)
                    wallet.coin += transaction.package.coin
                    wallet.save()

                    #
                    context = {
                        'tracking_code': transaction.tracking_code
                    }
                    return render(request, 'success_payment.html', context)
                elif t_status == 101:
                    context = {
                        'tracking_code': transaction.tracking_code
                    }
                    return render(request, 'error_payment.html', context)
                else:
                    return render(request, 'error_payment.html')
            else:
                return render(request, 'error_payment.html')

        else:
            return render(request, 'error_payment.html')

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bazar_myket(self, request, *args, **kwargs):
        package = Package.objects.get(id=request.data['package'])

        serializer = AddTransactionSerializer(data={'user': request.user.id,
                                                    'package': package.id,
                                                    'price': package.price,
                                                    'gateway': request.data['gateway'],
                                                    'gateway_code': ZarinpalCode.objects.last().code,
                                                    'description': 'خرید ' + package.name})
        if serializer.is_valid():
            transaction = serializer.save()
            transaction.state = Transaction.StateChoices.SUCCESS
            transaction.save()

            wallet = Wallet.objects.get(user=transaction.user)
            wallet.coin += transaction.package.coin
            wallet.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        avatar_id = request.data.get('avatar')
        if not avatar_id:
            return Response(data={"message": "please select avatar"}, status=status.HTTP_400_BAD_REQUEST)
        avatar = Avatar.objects.get(id=avatar_id)

        user = self.get_user()
        wallet = self.get_wallet()

        if wallet.coin < avatar.price:
            return Response(data={"message": "Not enough coin"}, status=status.HTTP_402_PAYMENT_REQUIRED)

        ownership = AvatarOwnerShip(user=user,
                                    avatar=avatar)
        ownership.save()

        wallet.coin = wallet.coin - avatar.price
        wallet.save()
        return Response(status=status.HTTP_200_OK)

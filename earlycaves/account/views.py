
import random
import logging
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from twilio.rest import Client
from rest_framework.parsers import MultiPartParser, FormParser

from . serializers import UserAcoountSerializer,PaymentLinkSerializer,CustomerSerializer,WhatappMarketingSerializer,EmailMarketingSerializer,TelegramChannelSerializer,GroupSerializer,LockMessagingSerializer,LockMessagingProductListSerializer,PaymentProductListSerializer,TelegramProductistSerializer,CustomerlistSerializer

from . models import User,PaymentProductQue,PaymentLink,EmailMarketing,WhatappMarketing,RazorPayPayment,Customer,TelegramChannelProduct,GroupName,LockMessaging,CashfreePayment
from asgiref.sync import async_to_sync
import json
import time
import threading
# Create your views here.
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import CreateChannelRequest,InviteToChannelRequest
from telethon.tl.functions.contacts import GetContactsRequest, ImportContactsRequest
from rest_framework.pagination import PageNumberPagination
from telethon.tl.types import InputPhoneContact
# from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import Channel
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import authentication_classes, permission_classes

import os
import razorpay
from django.conf import settings
from datetime import datetime
import uuid
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
import hmac
import hashlib
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


from django.shortcuts import render

def index(request):
    return render(request, 'out/index.html')

def signin(request):
    return render(request, 'sign-in.html')

def signup(request):
    return render(request, 'sign-up.html')

class UserAccountViewSet(viewsets.ViewSet):
    """
    login and signup class.
    """
    http_method_names = ['get', 'post', 'put', 'delete']
    def get_permissions(self):
            """Override permissions for specific actions."""
            if self.action in ["partial_update","get_user_details"]:
               return [IsAuthenticated()] 
            return [AllowAny()]
    

    def create(self, request):
        data=request.data

        email=request.data.get('email')
        mobile_no=request.data.get('phone_number')
        if email and mobile_no:
            try:
                is_exit=User.objects.get(Q(email=email) | Q(phone_number=mobile_no))
            except User.DoesNotExist:
                is_exit=None
        
            if is_exit:
                otp = random.randint(100000, 999999)
                is_exit.OTP=otp
                is_exit.save()
                response={"status":"success",'message':'User already exist'}
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                serializer=UserAcoountSerializer(data=data)
                if serializer.is_valid(raise_exception=False):
                    serializer.save()
                    response={"status":"success"}
                    return Response(response, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            response={"status":"Failed"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        

    def user_partial_update(self, request, pk=None):
        """Partially update the object"""
        username=request.data.get('username')
        first_name=request.data.get('first_name')
        profile_image=request.data.get('profile_image')
        data={'first_name':first_name,
              'username':username,
              }
        if profile_image:
            data['profile_image']=profile_image
        id=int(pk)
    
        try:
            instance=User.objects.get(id=id)
        except Exception as e:
            print(str(e))
            
        
        if not instance:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer=UserAcoountSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            response={"status":"success"}
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def get_otp(self, request):
        breakpoint()
        email=request.data.get('email')
        mobile_no=request.data.get('phone_number')
        if email or mobile_no:
            try:
                user_obj_exist = User.objects.filter(Q(email=email) | Q(phone_number=mobile_no))
            except User.DoesNotExist as e:
                response={'status':'failed'}
                return Response(response,status=status.HTTP_400_BAD_REQUEST)
            if user_obj_exist.first():
                otp = random.randint(100000, 999999)
                user_obj_exist = user_obj_exist.first()
                user_obj_exist.OTP=otp
                user_obj_exist.otp_create=datetime.now()
                mobile_no=user_obj_exist.phone_number
                self.send_otp(otp,mobile_no)
                user_obj_exist.save()
                response={"status":"success",'message':'OTP send Successfully '}
                return Response(response, status=status.HTTP_200_OK)
        else:
            response={"status":"Failed"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def login(self,request):
        email=request.data.get('email')
        mobile_no=request.data.get('phone_number')
        otp=request.data.get('OTP')
        if email or mobile_no:
            try:
                user_obj = User.objects.get(Q(email=email) | Q(phone_number=mobile_no))
            except User.DoesNotExist as e:
                response={'status':'failed'}
                return Response(response,status=status.HTTP_400_BAD_REQUEST)
            
            if user_obj.OTP==int(otp):
                token=Token.objects.get_or_create(user=user_obj)
                user_serailizer=UserAcoountSerializer(user_obj)
                token_key=token[0].key
                data=dict(user_serailizer.data)
                data['auth_token']=token_key
                response={'status':"success","data":data}
                return Response(response,status=status.HTTP_200_OK)
            else:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response={"status":"Failed"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)



    def send_otp(self,otp,mobile_number):
        url = f"https://control.msg91.com/api/v5/flow?authkey={settings.MSGI_Auth_key}&accept=application/json&content-type=application/json"

        payload = json.dumps({
        "template_id": "67d516e1d6fc057fee3354f2",
        "recipients": [
            {
            "mobiles": f"91{mobile_number}",
            "var1": otp
            }
        ]
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    @action(detail=False, methods=['get'])
    def get_user_details(self,request):
        user=request.user
       
        user_obj=User.objects.get(id=user.id)
        user_serilizer=UserAcoountSerializer(user_obj,many=False)
        return Response(user_serilizer.data, status=status.HTTP_200_OK)
        







GROQ_API_KEY = settings.GROQ_API_KEY
API_ID = settings.API_ID
API_HASH=settings.API_HASH




SESSION_DIR = os.path.join(settings.BASE_DIR, "telegram_sessions")
os.makedirs(SESSION_DIR, exist_ok=True)
SESSION_TIMERS = {}

class TelegramViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'])

    @staticmethod
    @sync_to_async
    def _create_group(mobile_number, phone_code_hash,user_id):
        return GroupName.objects.create(
            user_id=user_id,
            phone_number=mobile_number,
            phone_hash_code=phone_code_hash
        )
    
    @staticmethod
    @sync_to_async
    def _update_group(group_id,group_name, description,category):
        group_obj=GroupName.objects.get(id=group_id)
        group_obj.group_title=group_name
        group_obj.group_desc=description
        group_obj.category_id=category
        group_obj.save()
        return group_obj
       

    def get_telegram_otp(self, request):
        """ Step 1: Send a new OTP each time """
        
        mobile_number = request.data.get('phone_number')
        user_id=request.user.id

        if not mobile_number:
            return Response({"error": "Please enter a mobile number"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = async_to_sync(self._get_telegram_otp_async)(mobile_number,user_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def _get_telegram_otp_async(self, mobile_number,user_id):
        session_file = f"{SESSION_DIR}/session_{mobile_number}"
        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()
            result = await client.send_code_request(mobile_number)
            phone_code_hash = result.phone_code_hash

            group_obj = await self._create_group(mobile_number, phone_code_hash,user_id)

            return {
                "status": "success",
                "phone_code_hash": phone_code_hash,
                "group_obj_id": group_obj.id
            }

        finally:
            await client.disconnect()


    @action(detail=False, methods=['post'])
    def telegram_authentication(self, request):
        """ Step 2: Verify OTP & Save Session """
        mobile_number = request.data.get('phone_number')
        otp = request.data.get('OTP')
        phone_code_hash = request.data.get('phone_code_hash')
        group_id=request.data.get('group_obj_id')

        if not mobile_number or not otp or not phone_code_hash:
            return Response({"error": "Enter phone number, OTP, and phone_code_hash"}, status=status.HTTP_400_BAD_REQUEST)

        return async_to_sync(self._telegram_authentication_async)(mobile_number, otp, phone_code_hash,group_id)

    async def _telegram_authentication_async(self, mobile_number, otp, phone_code_hash,group_id):
        session_file = f"{SESSION_DIR}/session_{mobile_number}"
        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.sign_in(mobile_number, otp, phone_code_hash=phone_code_hash)
                await client.session.save()

            dialogs = await client.get_dialogs()
            groups = [dialog.name for dialog in dialogs if isinstance(dialog.entity, Channel)]

            return Response({"groups": groups,"group_obj_id":group_id}, status=status.HTTP_200_OK)

        except SessionPasswordNeededError:
            return Response({"error": "Two-step verification is enabled. Provide a password."}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        finally:
            await client.disconnect()

    @action(detail=False, methods=['post'])
    def telegram_group_create(self, request):
        """ Step 3: Create a Telegram Group """
        phone_number = request.data.get("phone_number")
        group_name = request.data.get("group_name")
        description = request.data.get("description", "")
        group_id=request.data.get('group_obj_id')
        category=request.data.get('categroy')
        category=int(category)
        group_id=int(group_id)

        if not phone_number or not group_name:
            return Response({"error": "Phone number and group name are required"}, status=400)
      
        return async_to_sync(self._telegram_group_create_async)(phone_number, group_name, description,group_id,category)

    async def _telegram_group_create_async(self, phone_number, group_name, description,group_id,category):
        session_file = f"{SESSION_DIR}/session_{phone_number}"
        if not os.path.exists(session_file + ".session"):
            return Response({"error": "User not authenticated. Verify OTP first."}, status=401)

        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()

            if client is None:
                return Response({"error": "Failed to initialize Telegram client"}, status=500)

            if not await client.is_user_authorized():
                return Response({"error": "User not authenticated. Verify OTP first."}, status=401)

           

            result = await client(CreateChannelRequest(
                title=group_name,
                about=description,
                megagroup=False  # ✅ True for groups, False for channels
            ))

            if result is None:
                print(f"❌ Telegram API returned None while creating group.")
                return Response({"error": "Failed to create group"}, status=500)


            group_obj = await self._update_group(group_id,group_name, description,category)
           
            serializer=GroupSerializer(group_obj)
            return Response({"data": serializer.data}, status=200)

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return Response({"error": str(e)}, status=500)

        finally:
            await client.disconnect()



    async def _get_user_id_by_phone_async(self, phone_number):
        session_file = f"{SESSION_DIR}/session_{phone_number}"
        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()

            if not await client.is_user_authorized():
                return Response({"error": "User not authenticated. Verify OTP first."}, status=401)

            contacts = await client.get_contacts()
            for contact in contacts:
                if contact.phone == phone_number:
                    return Response({"user_id": contact.id}, status=200)

            return Response({"error": "User not found in contacts"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        finally:
            await client.disconnect()


    @action(detail=False, methods=['post'])
    def created_group_add(self,request):
        group_name=request.data.get('group_name')
        phone_number=request.data.get('phone_number')
        category=request.data.get('category')
        group_desc=request.data.get('group_desc','')
        is_exist_group=GroupName.objects.filter(channel_name=group_name)
        if is_exist_group.count():
            group_serializer=GroupSerializer(is_exist_group,many=True)
            return Response({'data':group_serializer.data},status=status.HTTP_200_OK)
        else:
            telegram_group=GroupName.objects.create(channel_name=group_name,phone_number=phone_number,category_id=int(category),group_desc=group_desc)
            group_serializer=GroupSerializer(telegram_group,many=False)
            return Response(group_serializer.data,status=status.HTTP_200_OK)
       

    


class PaymentLinkViewSet(viewsets.ViewSet):
   
    parser_classes = [MultiPartParser, FormParser] 
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action in ["get_payment_product", "create_customer", "customer_verify"]:
            return [AllowAny()]  # Open access for this method
        return [IsAuthenticated()]


    def create(self, request):
        serializer = PaymentLinkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response({"message": "Payment link created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """Partially update the object"""
        
        data=request.data
        id=int(pk)
        try:
            instance=PaymentLink.objects.get(id=id)
        except Exception as e:
            print(str(e))
            
        
        if not instance:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer=PaymentLinkSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            response={"status":"success"}
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        user=request.user
        paginator = PageNumberPagination()
        paginator.page_size = 10
        payment_products=PaymentLink.objects.filter(user=user)
        result_page = paginator.paginate_queryset(payment_products, request)
        serializer = PaymentProductListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def get_payment_link(self,request):
        payment_product_id=request.GET.get('payment_product_id')
        if payment_product_id:
            payment_product_id=int(payment_product_id)
            try:
                payment_product=PaymentLink.objects.get(id=payment_product_id)
                uuid=payment_product.product_uuid
                base_url = request.build_absolute_uri('/')
                full_url=f"{base_url}account/payment/{uuid}"
                response={"status":"Sucess",'data':full_url}
                return Response(response,status=status.HTTP_200_OK)

            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            


    @action(detail=False, methods=['get'])
    def get_payment_product(self,request,uuid):
        payment_product_uuid=uuid
        if payment_product_uuid:
            try:
                payment_product=PaymentLink.objects.get(product_uuid=payment_product_uuid)
                payment_product_serializer=PaymentLinkSerializer(payment_product,many=False)
                response={"status":"Sucess",'data':payment_product_serializer.data}
                return Response(response,status=status.HTTP_200_OK)

            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response={"status":"Failed"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    



class EmailMarketingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def create(self, request):
        """Create an EmailMarketing entry."""
        serializer = EmailMarketingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def retrieve(self, request, pk=None):
        """Retrieve a specific EmailMarketing entry by ID."""
        try:
            email_marketing = EmailMarketing.objects.get(pk=pk)
            serializer = EmailMarketingSerializer(email_marketing)
            return Response(serializer.data)
        except EmailMarketing.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        



class WhatappMarketingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def create(self, request):
        """Create a WhatappMarketing entry."""
        serializer = WhatappMarketingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def retrieve(self, request, pk=None):
        """Retrieve a specific WhatappMarketing entry by ID."""
        try:
            marketing_entry = WhatappMarketing.objects.get(pk=pk)
            serializer = WhatappMarketingSerializer(marketing_entry)
            return Response(serializer.data)
        except WhatappMarketing.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        



class RazorpayViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling Razorpay payment operations.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = razorpay.Client(auth=('rzp_test_3Ov8h57M4j1VuZ', 'iIurT6eOniDDar0ZhuuIJnOW'))

    @action(detail=False, methods=['post'])
    def create_order_razorpay(self, request):
        """
        Create an order in Razorpay
        """
        try:
            data = request.data
            amount = data.get("amount")  # Amount in paise (e.g., 50000 for ₹500)
            currency = data.get("currency", "INR")
            product_uuid=data.get('product_uuid')
            product_type=data.get('product_type')
            if product_uuid and product_type:
                if product_type=='payment':
                    try:
                        product_id=PaymentLink.objects.get(product_uuid=product_uuid).id
                        prod_content_type=ContentType.objects.get_for_model(PaymentLink)
                    except Exception as e:
                        print(str(e))
                if product_type=='telegram':
                    try:
                        product_id=TelegramChannelProduct.objects.get(product_uuid=product_uuid).id
                        prod_content_type=ContentType.objects.get_for_model(TelegramChannelProduct)
                    except Exception as e:
                        print(str(e))
                    
                if product_type=='lockmessage':
                    try:
                        product_id=LockMessaging.objects.get(product_uuid=product_uuid).id
                        prod_content_type=ContentType.objects.get_for_model(LockMessaging)
                    except Exception as e:
                        print(str(e))

               
            receipt_id=self.generate_unique_id()
         
            # receipt = data.get("receipt", "order_rcptid_11")

            order_data = {
                "amount": amount,
                "currency": currency,
                "receipt": receipt_id,
                "payment_capture": 1,  # Auto-capture payment
            }

            order = self.client.order.create(order_data)
            if order:
                RazorPayPayment.objects.create(reciept_id=receipt_id,order_id=order['id'],amount=order['amount'],currency=order['currency']
                                               ,content_type=prod_content_type,object_id=product_id)
            return Response(order, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """
        Verify the payment signature
        """

        try:
            data = request.data
            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            razorpay_signature = data.get("razorpay_signature")
            RAZORPAY_SECRET='iIurT6eOniDDar0ZhuuIJnOW'
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
            payment = RazorPayPayment.objects.get(order_id=razorpay_order_id)
            generated_signature = hmac.new(
                settings.RAZORPAY_SECRET.encode(),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()
            is_valid = self.client.utility.verify_payment_signature(params_dict)

            if is_valid:
                return Response({"message": "Payment Verified Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid Payment Signature"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def generate_unique_id(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Format: YYYYMMDDHHMMSS
        unique_part = uuid.uuid4().hex[:6]  # Get first 6 characters of a UUID
        unique_id = f"EARLY{timestamp}_{unique_part}"
        return unique_id
            


    def razorpay_webhook(request):
        try:
            payload = json.loads(request.body)
            event = payload.get("event")

            if event == "payment.captured":
                payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})

                # Save transaction details
                RazorPayPayment.objects.create(
                    transaction_id=payment_data.get("id"),
                    order_id=payment_data.get("order_id"),
                    payment_id=payment_data.get("id"),
                    amount=payment_data.get("amount") / 100,  # Convert paisa to INR
                    currency=payment_data.get("currency"),
                    status=payment_data.get("status"),
                    payment_method=payment_data.get("method"),
                    
                    # webhook_response=payload  # Store full response for debugging
                )
                return Response({"message": "Payment recorded"}, status=200)

            return Response({"message": "Event not handled"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        



class CashfreeViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling Cashfree payment operations.
    """
    
    # parser_classes = [MultiPartParser, FormParser]

    def __init__(self, **kwargs):
        # super().__init__(**kwargs)
        self.cadhfree_headers ={
                "Content-Type": "application/json",
                "x-client-id": settings.cashfree_client_id, 
                "x-client-secret": settings.cashfree_clinet_secret_key, 
                "x-api-version": "2023-08-01"
            }
        
 
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action =="cashfree_webhook":
            return [AllowAny()]  # Open access for this method
        return [IsAuthenticated()]

    @action(detail=False, methods=['POST'])
    def create_order_cashfree(self, request):
            """
            Create an order in Cashfree
            """
            try:
                data = request.data
                amount = float(data.get("amount"))
                currency = data.get("currency", "INR")
                customer = data.get("customer", "INR")
                

                product_uuid = data.get('product_uuid')
                product_type = data.get('product_type')
                product_id, prod_content_type = None, None
                
                if product_uuid and product_type:
                    try:
                        if product_type == 'payment':
                            product_id = PaymentLink.objects.get(product_uuid=product_uuid).id
                            prod_content_type = ContentType.objects.get_for_model(PaymentLink)
                        elif product_type == 'telegram':
                            product_id = TelegramChannelProduct.objects.get(product_uuid=product_uuid).id
                            prod_content_type = ContentType.objects.get_for_model(TelegramChannelProduct)
                        elif product_type == 'lockmessage':
                            product_id = LockMessaging.objects.get(product_uuid=product_uuid).id
                            prod_content_type = ContentType.objects.get_for_model(LockMessaging)
                    except Exception as e:
                        print(str(e))

                receipt_id = self.generate_unique_id()
                base_url = request.build_absolute_uri('/')
                
            
                order_data = {
                    "order_id": receipt_id,
                    "order_amount": amount,
                    "order_currency": currency,
                    "customer_details": {
                        "customer_id": customer,
                        "customer_name": data.get("customer_name", "Test User"),
                        "customer_email": data.get("customer_email", "test@example.com"),
                        "customer_phone": data.get("customer_phone", "9999999999"),
                    },
                
                    "order_meta": {
                        "return_url": data.get("return_url", f"{base_url}/payment_success"),
                    }
                }
        
                
                url = "https://sandbox.cashfree.com/pg/orders"
                response = requests.post(url, headers=self.cadhfree_headers, json=order_data)

                order_response = response.json()

                if response.status_code == 200:
                    CashfreePayment.objects.create(
                        receipt_id=receipt_id,
                        order_id=order_response["order_id"],
                        amount=amount,
                        currency=currency,
                        status="created",
                        content_type=prod_content_type,
                        object_id=product_id
                    )
                    return Response(order_response, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": order_response}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def cashfree_webhook(self, request):
        # Only process POST requests
        if request.method != 'POST':
            return Response({"message": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # Check the Content-Type of the incoming request
        # content_type = request.headers.get('Content-Type')
        # if content_type != 'application/json':
        #     logger.error(f"Unsupported Media Type: Expected 'application/json', got '{content_type}'")
        #     return Response({"message": "Unsupported Media Type"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # Log incoming request, but avoid logging sensitive payment info
        logger.info(f"Received request data: {request.data}")

        # Extract signature from headers
        received_signature = request.headers.get('x-cf-signature')
        if not received_signature:
            logger.error("No signature found in the headers.")
            return Response({"message": "Signature missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Get raw body
        raw_body = request.body

        # Secret key for validating the signature
        secret_key = 'cfsk_ma_test_5e662164605e6f0cb11c95c4469e7e2d_773b7b42'.encode('utf-8')
        expected_signature = self.calculate_signature(secret_key, raw_body)

        # Validate the signature
        if received_signature != expected_signature:
            logger.warning("Invalid signature: Received signature does not match expected signature.")
            return Response({"message": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Try parsing the JSON payload
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            return Response({"message": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract order_id and payment data from the payload
        order_id = data.get('order', {}).get('order_id')
        payment_data = data.get('payment', {})

        # Validate order_id
        if not order_id:
            logger.warning("Order ID missing in the payload.")
            return Response({"message": "Order ID missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve payment record from the database
        try:
            payment_obj = CashfreePayment.objects.get(order_id=order_id)
        except CashfreePayment.DoesNotExist:
            logger.warning(f"Payment record not found for order_id: {order_id}")
            return Response({"message": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the payment fields with the data received
        try:
            payment_obj.status = payment_data.get('payment_status', payment_obj.status)
            payment_obj.payment_id = payment_data.get('payment_id', payment_obj.payment_id)
            payment_obj.transaction_id = payment_data.get('cf_payment_id', payment_obj.transaction_id)  # 'cf_payment_id' may be there sometimes
            payment_obj.amount = payment_data.get('payment_amount', payment_obj.amount)
            payment_obj.payment_method = payment_data.get('payment_method', payment_obj.payment_method)

            # Update the captured status and time
            payment_obj.captured = payment_data.get('payment_status') == True  # Compare with boolean True
            payment_obj.captured_at = payment_data.get('payment_completion_time')

            # Update card info if available
            payment_obj.card_last4 = payment_data.get('card', {}).get('card_number', '')[-4:] if payment_data.get('card') else None
            payment_obj.bank_name = payment_data.get('bank', {}).get('bank_name') if payment_data.get('bank') else None
            payment_obj.upi_id = payment_data.get('upi', {}).get('upi_id') if payment_data.get('upi') else None

            # Save the entire webhook response for auditing purposes
            payment_obj.webhook_response = data

            # Save the updated payment record
            payment_obj.save()
        except Exception as e:
             logger.info(f"data issue: {str(e)}")

        logger.info(f"Webhook processed successfully for order_id: {order_id}")
        return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
    

    def generate_unique_id(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_part = uuid.uuid4().hex[:6]
        return f"CASHFREE{timestamp}_{unique_part}"






class TelegramChannelViewSet(viewsets.ViewSet):
   
    parser_classes = [MultiPartParser, FormParser] 
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action in ["get_payment_product" or "create_customer" or "customer_verify"]:
            return [AllowAny()]  # Open access for this method
        return [IsAuthenticated()]


    def create(self, request):
        
        serializer = TelegramChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({"message": "Telegram channel created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def get_telegram_grouplist(self, request):
        user=request.user
        paginator = PageNumberPagination()
        paginator.page_size = 10
        group_list=GroupName.objects.filter(user=user).values_list('id',flat=True)
        payment_products=TelegramChannelProduct.objects.filter(group_id__in=group_list)
        result_page = paginator.paginate_queryset(payment_products, request)
        serializer = TelegramProductistSerializer(result_page, many=True)
    
        return paginator.get_paginated_response(serializer.data) 


            


    @action(detail=False, methods=['get'])
    def get_telegramchannel_product(self,request,uuid):
        payment_product_uuid=uuid
        if payment_product_uuid:
            try:
                payment_product=TelegramChannelProduct.objects.get(product_uuid=payment_product_uuid)
                payment_product_serializer=TelegramChannelSerializer(payment_product,many=False)
                response={"status":"Sucess",'data':payment_product_serializer.data}
                return Response(response,status=status.HTTP_200_OK)

            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response={"status":"Failed"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    

import asyncio

class CustomerView(viewsets.ViewSet):
    permission_classes=[AllowAny]
    @action(detail=False, methods=['post'])
    def create_customer(self,request,):
        data = request.data.copy()  
        product_id=request.data.get('product_id')
        product_type=request.data.get('product_type')
        phone=request.data.get('phone')
        if product_id and product_type=='payment':
            try:
                product_obj=PaymentLink.objects.get(id=product_id)
                prod_content_type=ContentType.objects.get_for_model(PaymentLink)
            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            data["object_id"] = product_obj.id # Example additional field
            data["content_type"] = prod_content_type.id
            customer_serializer = CustomerSerializer(data=data)
        elif product_id and product_type=='telegram':
            try:
                product_obj=TelegramChannelProduct.objects.get(id=product_id)
        
                prod_content_type=ContentType.objects.get_for_model(TelegramChannelProduct).id
            except Exception as e:
                response={"status":str(e)}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            data["object_id"] = product_obj.id # Example additional field
            data["content_type"] = prod_content_type
            customer_serializer = CustomerSerializer(data=data)
        
        elif product_id and product_type=='lockmessage':
            try:
                product_obj=LockMessaging.objects.get(id=product_id)
                prod_content_type=ContentType.objects.get_for_model(LockMessaging).id
            except Exception as e:
                response={"status":str(e)}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
           
            data["object_id"] = product_obj.id # Example additional field
            data["content_type"] = prod_content_type
            customer_serializer = CustomerSerializer(data=data)


        else:
            response={"status":"Failed"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
       
        is_exist=self.is_verified(phone,prod_content_type,product_obj.id)
        if is_exist:
           customer_serializer=CustomerSerializer(is_exist,many=False)
           return Response(customer_serializer.data, status=status.HTTP_201_CREATED)        

        if customer_serializer.is_valid():
            otp = random.randint(100000, 999999)
            now_time=datetime.now()
            customer_serializer.save(OTP=otp,otp_create=now_time)
            self.send_otp(otp,phone)
            return Response(customer_serializer.data, status=status.HTTP_201_CREATED)
        return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False,methods=['post'])
    def customer_verify(self,request):
        customer_id=request.data.get('customer_id')
        otp=request.data.get('otp')
        print(otp,customer_id)
        if customer_id and otp:
            customer_id=int(customer_id)
            try:
                customer_obj=Customer.objects.get(id=customer_id)
                if customer_obj.OTP==int(otp):
                    content_type_id=int(customer_obj.content_type_id)
                    content_class = ContentType.objects.get(id=content_type_id)
                    model_class =content_class.model_class()
                    product_obj=model_class.objects.get(id=customer_obj.object_id)
                    # self.add_user_to_group("+918209054104","+918171275374","karmaproduct")
                    data={'product_uuid':product_obj.product_uuid,'amount':product_obj.price,'discount': None if model_class==LockMessaging else product_obj.discount }
                    response={"status":"Sucess",'data':data}
                    return Response(response,status=status.HTTP_200_OK)
                else:
                    response={"status":"Failed",'message':"OTP does not match"}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                response={"status":"Failed",'message':str(e)}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response={"status":"Failed"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)   

    
    def is_verified(self,phone,content_type,object_id):
        is_exist=Customer.objects.filter(phone=phone,content_type=content_type,object_id=object_id)
        if is_exist.count():
            is_exist=is_exist[0]
            is_exist.is_verified=True
            is_exist.save()   

            return is_exist
        else:
            return False
    
    def send_otp(self,otp,mobile_number):
    
        url = "https://control.msg91.com/api/v5/flow?authkey=443227AlKikWdkmls67d510daP1&accept=application/json&content-type=application/json"
        print(mobile_number,'----------------------------')
        payload = json.dumps({
        "template_id": "67d516e1d6fc057fee3354f2",
        "recipients": [
            {
            "mobiles": f"91{mobile_number}",
            "var1": otp
            }
        ]
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    

    
    def add_user_to_group(self, admin_phone, user_phone, group_name):
        """ Wrapper function to fetch group ID and add user """
        group_id = async_to_sync(self._get_group_id_async)(admin_phone, group_name)
        if not group_id:
            return {"error": "Group not found"}
        print(f"📞 Admin: {admin_phone} | User: {user_phone} | Group ID: {group_id}")
        return async_to_sync(self._add_user_to_selected_group_async)(admin_phone, user_phone, group_id)

    async def _get_group_id_async(self, admin_phone, group_name):
        """ Fetch group ID from the Telegram account """
        session_file = os.path.join(SESSION_DIR, f"session_{admin_phone}")
        API_ID="26553278"
        API_HASH="1ba4cb64bb38d956faf3f2a33b2a0bba"
        print(session_file,'---------')
        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                return {"error": "Admin is not authenticated. Verify OTP first."}

            print(f"✅ Connected: Fetching group '{group_name}' for {admin_phone}")

            # ✅ Get all group chats
            dialogs = await client.get_dialogs()
            groups = [chat for chat in dialogs if chat.is_group]

            # ✅ Find the group by name or username
            group = next(
                (chat for chat in groups if chat.name == group_name or getattr(chat.entity, "username", None) == group_name),
                None
            )
            if not group:
                print(f"❌ Group '{group_name}' not found.")
                return None  # Return None if group is not found

            print(f"✅ Group found: {group.name} (ID: {group.entity.id})")
            return group.entity.id  # Return group ID

        except Exception as e:
            print(f"❌ Error in _get_group_id_async: {e}")
            return {"error": str(e)}
        finally:
            await client.disconnect()

    async def _add_user_to_selected_group_async(self, admin_phone, user_phone, group_id):
        """ Asynchronous function to add user to a specific Telegram group """
        session_file = os.path.join(SESSION_DIR, f"session_{admin_phone}")
        API_ID = "26553278"
        API_HASH = "1ba4cb64bb38d956faf3f2a33b2a0bba"
        client = TelegramClient(session_file, API_ID, API_HASH)

        try:
            await client.connect()
            print(f"✅ Connected: Adding {user_phone} to group {group_id}")

            if not await client.is_user_authorized():
                return {"error": "Admin is not authenticated. Verify OTP first."}

            # ✅ Step 1: Get the User ID by Phone Number
            try:
                contacts = await asyncio.wait_for(client(GetContactsRequest(hash=0)), timeout=30)
                print(f"✅ Contacts fetched: {len(contacts.users)} users found.")
            except asyncio.TimeoutError:
                print("❌ Request timed out while fetching contacts!")
                return {"error": "Timeout while fetching contacts"}
            except Exception as e:
                print(f"❌ Error fetching contacts: {e}")
                return {"error": str(e)}

            # Debugging: Print all contacts' phone numbers
            for contact in contacts.users:
                print(f"👤 Contact found: {contact.phone}")

            # Ensure `user_phone` is not None
            if not user_phone:
                print("❌ Error: user_phone is None!")
                return {"error": "User phone number is missing"}

            # Find user in contacts
            user = next(
                (contact for contact in contacts.users if contact.phone and contact.phone.lstrip("+") == user_phone.lstrip("+")), 
                None
            )

            if not user:
                print(f"🔍 User {user_phone} not found in contacts. Importing...")
                try:
                    result = await client(ImportContactsRequest([
                        InputPhoneContact(client_id=0, phone=user_phone, first_name="User", last_name="")
                    ]))
                    if result.users:
                        user = result.users[0]
                        print(f"✅ User imported: {user.id}")
                    else:
                        print(f"❌ User {user_phone} not found after import.")
                        return {"error": "User not found or not on Telegram"}
                except Exception as e:
                    print(f"❌ Error importing user: {e}")
                    return {"error": str(e)}

            # ✅ Step 2: Get the specific group
            try:
                group_entity = await client.get_entity(group_id)
                print(f"✅ Group entity found: {group_entity.title}")
            except Exception:
                print("❌ Group not found!")
                return {"error": "Group not found"}

            # ✅ Step 3: Add user to the group
            try:
                await client(InviteToChannelRequest(channel=group_entity, users=[user.id]))
                print(f"✅ User {user_phone} added to group {group_id}")
                return {"message": f"User {user_phone} added to group {group_id}"}
            except Exception as e:
                if "PEER_FLOOD" in str(e):
                    return {"error": "Too many invites sent. Try again later."}
                elif "USER_PRIVACY_RESTRICTED" in str(e):
                    return {"error": "User has restricted who can add them to groups."}
                elif "CHAT_ADMIN_REQUIRED" in str(e):
                    return {"error": "Bot must be an admin to add users to this group."}
                print(f"❌ Error adding user to group: {e}")
                return {"error": str(e)}

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"error": str(e)}
        finally:
            await client.disconnect()
            print("🔌 Disconnected from Telegram")




class LockMessagingViewSet(viewsets.ViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action == "get_lockmessage_product":
            return [AllowAny()]  # Open access for this method
        return [IsAuthenticated()]

    def create(self, request):
            serializer = LockMessagingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def list(self, request):
        user=request.user
        paginator = PageNumberPagination()
        paginator.page_size = 10
        lock_messages=LockMessaging.objects.filter(user=user)
        result_page = paginator.paginate_queryset(lock_messages, request)
        serializer = LockMessagingProductListSerializer(result_page, many=True,context={'request':request})
        return paginator.get_paginated_response(serializer.data)
        

    def update(self, request, pk=None):
        # Your custom logic to update a resource with ID `pk`
        # For example:
        try:
            obj = LockMessaging.objects.get(pk=pk)  # replace with your model
        except LockMessaging.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LockMessagingSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print("DELETE hit")
        obj = get_object_or_404(LockMessaging, pk=pk)
        obj.delete()
        response={"status":"success"}
        return Response(response,status=status.HTTP_204_NO_CONTENT)

    
    
    @action(detail=False, methods=['get'])
    def get_lockmessage_link(self,request):
        lockmessage_id=request.GET.get('lockmessage_id')
        if lockmessage_id:
            lockmessage_id=int(lockmessage_id)
            try:
                lock_product=LockMessaging.objects.get(id=lockmessage_id)
                uuid=lock_product.product_uuid
                base_url = request.build_absolute_uri('/')
                full_url=f"{base_url}account/lockmessage/{uuid}"
                response={"status":"Sucess",'data':full_url}
                return Response(response,status=status.HTTP_200_OK)

            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            


    @action(detail=False, methods=['get'])
    def get_lockmessage_product(self,request,uuid):
        lock_product_uuid=uuid
        if lock_product_uuid:
            try:
                lock_product=LockMessaging.objects.get(product_uuid=lock_product_uuid)
                lock_product_serializer=LockMessagingSerializer(lock_product,many=False)
                response={"status":"Sucess",'data':lock_product_serializer.data}
                return Response(response,status=status.HTTP_200_OK)

            except Exception as e:
                response={"status":"Failed"}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response={"status":"Failed"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    


class AnalyticsView(viewsets.ViewSet):
    def list(self,request):
        user=request.user
        paginator = PageNumberPagination()
        paginator.page_size = 10
        payment_products=PaymentLink.objects.filter(user=user).values_list('id')
        content_type=ContentType.objects.get_for_model(PaymentLink)
        payment_customers=Customer.objects.filter(object_id__in=payment_products,content_type=content_type)

        payment_products=LockMessaging.objects.filter(user=user).values_list('id')
        content_type=ContentType.objects.get_for_model(LockMessaging)
        lock_customers=Customer.objects.filter(object_id__in=payment_products,content_type=content_type)

        groups_id=GroupName.objects.filter(user=user).values_list('id',flat=True)
        payment_products=TelegramChannelProduct.objects.filter(group_id__in=groups_id).values_list('id')
        content_type=ContentType.objects.get_for_model(PaymentLink)
        telegram_customers=Customer.objects.filter(object_id__in=payment_products,content_type=content_type)

        final_list=payment_customers|lock_customers|telegram_customers
        result_page = paginator.paginate_queryset(final_list, request)
        serializer = CustomerlistSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



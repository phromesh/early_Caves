
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from multiselectfield import MultiSelectField


def user_image(instance,filename):
    id=instance.user
    title=instance.first_name
    return f"file/profile_image/{id}/{title}/{filename}"

def payment_product(instance,filename):
    id=instance.user
    title=instance.title
    return f"file/paymentproduct/{id}/{title}/{filename}"

def payment_product_banner(instance,filename):
    id=instance.user
    title=instance.title
    return f"file/paymentproductbanner/{id}/{title}/{filename}"


def lock_message_file(instance,filename):
    id=instance.user
    title=instance.title
    return f"file/lockmessage_file/{id}/{filename}"

def lock_message_image(instance,filename):
    id=instance.user
    title=instance.title
    return f"file/lockmessage_image/{id}/{filename}"

def lock_message_video(instance,filename):
    id=instance.user
    title=instance.title
    return f"file/lockmessage_video/{id}/{filename}"


def telegram_product_banner(instance,filename):
    id=instance.id
    title=instance.title
    return f"file/paymentproductbanner/{id}/{title}/{filename}"

def email_market(instance,filename):
    id=instance.user
    return f"file/emailmarket_csv/{id}/{filename}"

def whatapp_market(instance,filename):
    id=instance.user
  
    return f"file/whatapp_csv/{id}/{filename}"

def email_send_file(instance,filename):
    id=instance.user
    return f"file/email_send_file/{id}/{filename}"

def whatapp_send_file(instance,filename):
    id=instance.user
    return f"file/whatapp_send_file/{id}/{filename}"

class ClientGoal(models.Model):
    text=models.CharField(max_length=250)

    def __str__(self):
        return str(self.text)


class CourseField(models.Model):
    text=models.CharField(max_length=50)
   


class User(AbstractUser):
    ROLE =( 
    ("Admin", "admin"), 
    ("Client", "client"), 
     
    ) 
    role= models.CharField(max_length=30,choices=ROLE)
    clientgoal=models.ForeignKey(ClientGoal,on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(
        max_length=15,  # Adjust length as needed
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],  # Allows optional "+" and 9-15 digits
        blank=True,
        null=True,
        unique=True
    )
    OTP=models.IntegerField(default=None,null=True)
    otp_create=models.DateTimeField(null=True)
    username=models.CharField(max_length=50,null=True,blank=True,unique=False)
    email = models.EmailField(unique=True)
    profile_image=models.ImageField(upload_to=user_image,null=True)

    USERNAME_FIELD = "email"  # Use email as the login field
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class GroupName(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,  # Adjust length as needed
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],  # Allows optional "+" and 9-15 digits
        blank=True,
        null=True,
    )
    channel_name= models.CharField(max_length=50)
    category   = models.ForeignKey(CourseField,on_delete=models.SET_NULL,null=True)
    group_title= models.CharField(max_length=250,null=True)
    group_desc = models.TextField()
    phone_hash_code=models.CharField(max_length=50,null=True)
    create_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TelegramChannelProduct(models.Model):
    group=models.ForeignKey(GroupName,on_delete=models.SET_NULL,null=True)
    title=models.CharField(max_length=300)
    desc=models.TextField()
    category=models.ForeignKey(CourseField,on_delete=models.SET_NULL,null=True)
    banner_img=models.ImageField(upload_to=telegram_product_banner,null=True)
    price=models.IntegerField(null=True)
    discount=models.IntegerField(null=True)
    gst_info=models.BooleanField(default=False)
    product_uuid=models.UUIDField(default =uuid.uuid4)
    status=models.BooleanField(default=False)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)




class TelegramProductQue(models.Model):
    product=models.ForeignKey(TelegramChannelProduct,on_delete=models.CASCADE)
    text=models.CharField(max_length=300)




class SubscribePlan(models.Model):
    group =models.ForeignKey(TelegramChannelProduct,on_delete=models.CASCADE)
    plan_name=models.CharField(max_length=50,null=True)
    life_time=models.BooleanField(default=False)
    duration_days = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class PaymentLink(models.Model):
    CHOICES = (
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=250)
    banner_img=models.ImageField(upload_to=payment_product_banner)
    desc=models.TextField()
    price= models.IntegerField()
    discount=models.IntegerField()
    thank_note=models.TextField()
    redirect_url=models.URLField()
    googel_pixel_id=models.CharField(max_length=150,null=True)
    facebook_pixel_id=models.CharField(max_length=150,null=True)
    email=models.EmailField()
    phone_number=models.CharField(max_length=15)
    gst_info=models.BooleanField(default=False)
    media_url=models.FileField(upload_to=payment_product)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    product_uuid=models.UUIDField(default =uuid.uuid4)
    status=models.CharField(choices=CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="payment_approved_by")
    approved_date = models.DateTimeField(blank=True, null=True)
    

class PaymentProductQue(models.Model):
    product=models.ForeignKey(PaymentLink,on_delete=models.CASCADE)
    text=models.CharField(max_length=300)


class Customer(models.Model):
    phone=models.CharField(max_length=15,null=True)
    email=models.EmailField(null=True)
    create_at=models.DateTimeField(auto_now_add=True)
    subscribe_start=models.DateTimeField(auto_now_add=True,null=True)
    subscribe_end=models.DateTimeField(null=True)
    subscribeplan=models.ForeignKey(SubscribePlan,on_delete=models.SET_NULL,null=True)
    OTP=models.IntegerField(default=None,null=True)
    otp_create=models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    is_verified=models.BooleanField(default=False)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')



class CustomerPaymentProductAns(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    question=models.ForeignKey(PaymentProductQue,on_delete=models.SET_NULL,null=True)
    answer= models.CharField(max_length=300,null=True)
    create_at=models.DateTimeField(auto_now_add=True)


class CustomerTelegramProductAns(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    question=models.ForeignKey(TelegramChannelProduct,on_delete=models.SET_NULL,null=True)
    answer= models.CharField(max_length=300,null=True)
    create_at=models.DateTimeField(auto_now_add=True)



class EmailMarketing(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    email_csv_file=models.FileField(upload_to=email_market)
    desc= models.TextField(null=True)
    send_file=models.FileField(upload_to=email_send_file)
    create_at=models.DateTimeField(auto_now_add=True)



class WhatappMarketing(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    contact_csv_file=models.FileField(upload_to=whatapp_market)
    desc= models.TextField(null=True)
    send_file=models.FileField(upload_to=whatapp_send_file)
    create_at=models.DateTimeField(auto_now_add=True)





class RazorPayPayment(models.Model):
    
    TRANSACTION_STATUS_CHOICES = [
        ('created', 'Created'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
        ('emi', 'EMI'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    user=models.ForeignKey(Customer,on_delete=models.DO_NOTHING,null=True, help_text="Razorpay payment ID")
    reciept_id=models.CharField(max_length=30,unique=True)
    transaction_id = models.CharField(max_length=100, null=True, help_text="Unique Razorpay transaction ID")
    order_id = models.CharField(max_length=100, help_text="Associated order ID from Razorpay")
    payment_id = models.CharField(max_length=100, null=True, help_text="Razorpay payment ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in INR")
    currency = models.CharField(max_length=10, default="INR", help_text="Currency of transaction")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, help_text="Transaction status")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text="Payment method used")
    captured_at = models.DateTimeField(null=True, blank=True, help_text="Payment capture timestamp")
    captured = models.BooleanField(default=False)
    refund_status = models.BooleanField(default=False, help_text="True if refunded")
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Razorpay transaction fee")
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Tax amount deducted")
    card_last4 = models.CharField(max_length=4, null=True, blank=True, help_text="Last 4 digits of card (if applicable)")
    bank_name = models.CharField(max_length=100, null=True, blank=True, help_text="Bank name (if net banking)")
    upi_id = models.CharField(max_length=100, null=True, blank=True, help_text="UPI ID (if paid via UPI)")
    notes = models.TextField(null=True, blank=True, help_text="Additional transaction notes")
    webhook_response = models.JSONField(null=True, blank=True, help_text="Raw webhook response from Razorpay")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, help_text="Transaction creation time")

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"
    






class CashfreePayment(models.Model):
    
    TRANSACTION_STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
        ('emi', 'EMI'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True, help_text="Cashfree user ID")
    receipt_id = models.CharField(max_length=30, unique=True, help_text="Unique receipt ID for Cashfree")
    transaction_id = models.CharField(max_length=100, null=True, help_text="Unique Cashfree transaction ID")
    order_id = models.CharField(max_length=100, help_text="Associated order ID from Cashfree")
    payment_id = models.CharField(max_length=100, null=True, help_text="Cashfree payment ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in INR")
    currency = models.CharField(max_length=10, default="INR", help_text="Currency of transaction")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, help_text="Transaction status")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text="Payment method used")
    captured_at = models.DateTimeField(null=True, blank=True, help_text="Payment capture timestamp")
    captured = models.BooleanField(default=False)
    refund_status = models.BooleanField(default=False, help_text="True if refunded")
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cashfree transaction fee")
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Tax amount deducted")
    card_last4 = models.CharField(max_length=4, null=True, blank=True, help_text="Last 4 digits of card (if applicable)")
    bank_name = models.CharField(max_length=100, null=True, blank=True, help_text="Bank name (if net banking)")
    upi_id = models.CharField(max_length=100, null=True, blank=True, help_text="UPI ID (if paid via UPI)")
    notes = models.TextField(null=True, blank=True, help_text="Additional transaction notes")
    webhook_response = models.JSONField(null=True, blank=True, help_text="Raw webhook response from Cashfree")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, help_text="Transaction creation time")

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"


class LockMessaging(models.Model):
    CHOICES = (
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    )
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    title=models.CharField(max_length=250,null=True)
    product_file=models.FileField(upload_to=lock_message_file,null=True)
    product_img=models.ImageField(upload_to=lock_message_image,null=True)
    product_video=models.FileField(upload_to=lock_message_video,null=True)
    desc=models.TextField(null=True)
    price=models.CharField(default=True)
    categroy=models.ForeignKey(CourseField,on_delete=models.SET_NULL,null=True)
    product_uuid=models.UUIDField(default =uuid.uuid4)
    create_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(choices=CHOICES, default="pending")
    expire=models.DateTimeField(null=True)
    update=models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="lock_approved_by")
    approved_date = models.DateTimeField(blank=True, null=True)


class EmailMarketing(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    email_csv_file=models.FileField(upload_to=email_market)
    desc= models.TextField(null=True)
    send_file=models.FileField(upload_to=email_send_file)
    create_at=models.DateTimeField(auto_now_add=True)



class WhatappMarketing(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    contact_csv_file=models.FileField(upload_to=whatapp_market)
    desc= models.TextField(null=True)
    send_file=models.FileField(upload_to=whatapp_send_file)
    create_at=models.DateTimeField(auto_now_add=True)


class PunchInUser(models.Model):
    COMMISSION_CHOICES  = (
        ('other_payment_mode', 'OTHER PAYMENT MODE'),
        ('upi', 'UPI'),
    )
    FEATURE_CHOICES = (
        ("payment_link", "PAYMENT_LINK"),
        ("telegram", "TELEGRAM"),
        ("lock_message", "LOCK_MESSAGE")
    )
    ACQUISITION_CHOICES = (
        ('self', "SELF"),
        ('organic', 'ORGANIC')
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="punch_user")
    creator_name = models.CharField(max_length=20)
    creator_id = models.CharField(max_length=20)
    commission_options = models.CharField(choices=COMMISSION_CHOICES, default="upi")
    commission_percent = models.CharField(max_length=20)
    minimum_ticket = models.FloatField()
    maximum_ticket = models.FloatField()
    feature_type = MultiSelectField(choices=FEATURE_CHOICES)
    social_link = models.TextField()
    acquisition_funnel = models.CharField(choices=ACQUISITION_CHOICES, default="self")
    onboarding_reason = models.TextField()
    whatsapp_group = models.CharField(max_length=100)
    document_name = models.CharField(max_length=20)
    document = models.FileField(upload_to="punch_in_documents")
    notes = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="punch_created_by")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
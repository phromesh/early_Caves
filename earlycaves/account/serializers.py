from . models import User,PaymentLink,PaymentProductQue,Customer,CustomerTelegramProductAns,CustomerPaymentProductAns,EmailMarketing,WhatappMarketing,TelegramChannelProduct,TelegramProductQue,GroupName,LockMessaging,RazorPayPayment,SubscribePlan

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
import json
from django.db.models import Count, Sum



class UserAcoountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','email','clientgoal','phone_number','profile_image']


   

class PaymentProductQueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProductQue
        fields = ['id', 'text'] 



class PaymentLinkSerializer(serializers.ModelSerializer):
    questions = serializers.CharField(required=False)
    questions_data=serializers.SerializerMethodField('get_qeustion_data')
    class Meta:
        model = PaymentLink
        exclude =['user']

       
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])  # Extract nested data
        payment_link = PaymentLink.objects.create(**validated_data)
        if questions_data:
            questions_data=questions_data.split(',')
            # Create related PaymentProductQue records
            for question in questions_data:
                PaymentProductQue.objects.create(product=payment_link, text=question)

        return payment_link
    

    def get_qeustion_data(self,obj):
        payment_proudcut_id=obj.id
        questions=PaymentProductQue.objects.filter(product_id=payment_proudcut_id)
        data=PaymentProductQueSerializer(questions,many=True).data
        return data
    


    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)  # Get updated questions

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if questions_data is not None:
            questions_data = questions_data.split(',')
            PaymentProductQue.objects.filter(product=instance).delete()
            for question in questions_data:
                PaymentProductQue.objects.create(product=instance, text=question)

        return instance

    def get_question_data(self, obj):
        payment_product_id = obj.id
        questions = PaymentProductQue.objects.filter(product_id=payment_product_id)
        data = PaymentProductQueSerializer(questions, many=True).data
        return data
    

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=GroupName
        fields=['id','category','group_title','group_desc','phone_number','channel_name']

class TelegramCustomerProductAnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTelegramProductAns
        fields = ['question', 'answer'] 


class CustomerProductAnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPaymentProductAns
        fields = ['question', 'answer'] 


class CustomerSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(child=serializers.CharField(),required=False)
    # answers = CustomerProductAnsSerializer(many=True, write_only=True)  # Nested field for answers

    class Meta:
        model = Customer
        exclude=['OTP']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        customer = Customer.objects.create(**validated_data)
        if len(answers_data)==0:
            return customer
        answers_data=json.loads(answers_data[0])
        content_type_id=validated_data['content_type']
        content_class = ContentType.objects.get(id=content_type_id.id)
        model_class =content_class.model_class()

        
        for ans_data in answers_data:
            question_id=list(ans_data.keys())[0]
            answer=ans_data[question_id]
            if model_class==PaymentLink:
                CustomerPaymentProductAns.objects.create(customer=customer,question_id=int(question_id),answer=answer)
            elif model_class==TelegramChannelProduct:
                 CustomerTelegramProductAns.objects.create(customer=customer,question_id=int(question_id),answer=answer)

        return customer
    


class EmailMarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMarketing
        fields = ['email_csv_file','send_file','desc']




class WhatappMarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatappMarketing
        fields = ['contact_csv_file','send_file','desc']







class TelegramProductQueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProductQue
        fields = ['id', 'text'] 



class TelegramChannelSerializer(serializers.ModelSerializer):
    questions = serializers.CharField(required=False)
    questions_data=serializers.SerializerMethodField('get_qeustion_data')
    subscrible_plan=serializers.IntegerField(required=False)
    subscrible_plan_name=serializers.CharField(required=False)
    subscribe_plan_id=serializers.SerializerMethodField('get_subscribe_plan')
    class Meta:
        model = TelegramChannelProduct
        fields = '__all__'

       
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])  # Extract nested data
        subscrible_plan=validated_data.pop('subscrible_plan','')
        subscrible_plan_name=validated_data.pop('subscrible_plan_name','')
        telegram_product = TelegramChannelProduct.objects.create(**validated_data)
        questions_data=questions_data.split(',')
        # Create related PaymentProductQue records
        for question in questions_data:
            TelegramProductQue.objects.create(product=telegram_product, text=question)

        if subscrible_plan:
            SubscribePlan.objects.create(group=telegram_product,plan_name=subscrible_plan_name,duration_days=subscrible_plan)

        return telegram_product
    

    def get_qeustion_data(self,obj):
        payment_proudcut_id=obj.id
        questions=TelegramProductQue.objects.filter(product_id=payment_proudcut_id)
        data=TelegramProductQueSerializer(questions,many=True).data
        return data
    

    def get_subscribe_plan(self,obj):
        telegram_group=obj.id
        try:
            subscribe_obj=SubscribePlan.objects.get(group=telegram_group)
        except:
            subscribe_obj=None
        if subscribe_obj:
            return subscribe_obj.id
        else:
            return None





class TelegramCustomerSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(child=serializers.CharField(),required=False)
    # answers = CustomerProductAnsSerializer(many=True, write_only=True)  # Nested field for answers

    class Meta:
        model = Customer
        exclude=['OTP']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        answers_data=json.loads(answers_data[0])

        customer = Customer.objects.create(**validated_data)
        for ans_data in answers_data:
            question_id=list(ans_data.keys())[0]
            answer=ans_data[question_id]
            CustomerTelegramProductAns.objects.create(customer=customer,question_id=int(question_id),answer=answer)
        return customer
    



class LockMessagingSerializer(serializers.ModelSerializer):
    # =serializers.SerializerMethodFielsale_countd('get_sale_count',read_only=True)
    # revenue=serializers.SerializerMethodField('get_revenue',read_only=True)



    class Meta:
        model = LockMessaging
        fields = ['id','title','product_file','product_img','product_video','desc','price','expire','categroy']






class LockMessagingProductListSerializer(serializers.ModelSerializer):
    sale_count=serializers.SerializerMethodField('get_sale_count')
    revenue=serializers.SerializerMethodField('get_revenue')
    product_link=serializers.SerializerMethodField('get_product_link',read_only=True)
    


    class Meta:
        model = LockMessaging
        fields = ['id','title','product_file','status','product_uuid','product_img','product_video','price','expire','sale_count','revenue','product_link']
        

    def get_sale_count(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    total_sale=Count('id'),
                    # total_revenue=Sum('amount')
                )
        razor_obj
        return razor_obj
    
    def get_revenue(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    # total_sale=Count('id'),
                    total_revenue=Sum('amount')
                )
        razor_obj
       
        return razor_obj
    

    def get_product_link(self,obj):
        print(self.__dict__)
        request=self.context.get('request')
        lock_product=LockMessaging.objects.get(id=obj.id)
        uuid=lock_product.product_uuid
        base_url = request.build_absolute_uri('/')
        full_url=f"{base_url}account/payment/{uuid}"
        return full_url
    



    
class PaymentProductListSerializer(serializers.ModelSerializer):
    sale_count=serializers.SerializerMethodField('get_sale_count')
    revenue=serializers.SerializerMethodField('get_revenue')
    


    class Meta:
        model = PaymentLink
        fields = ['id','title','price','product_uuid','status','sale_count','revenue']
        

    def get_sale_count(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    total_sale=Count('id'),
                    # total_revenue=Sum('amount')
                )
        razor_obj
        if razor_obj:
            return None
        else:
            return razor_obj
    
    def get_revenue(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    # total_sale=Count('id'),
                    total_revenue=Sum('amount')
                )
        razor_obj
        if razor_obj:
            return None
        else:
            return razor_obj
    




    
class TelegramProductistSerializer(serializers.ModelSerializer):
    sale_count=serializers.SerializerMethodField('get_sale_count')
    revenue=serializers.SerializerMethodField('get_revenue')
    group_name=serializers.SerializerMethodField('get_group_name')
    


    class Meta:
        model = TelegramChannelProduct
        fields = ['id','title','price','group_name','status','sale_count','revenue']
        

    def get_sale_count(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    total_sale=Count('id'),
                    # total_revenue=Sum('amount')
                )
        razor_obj
        return razor_obj
    
    def get_sale_count(self,obj):
        object_id=obj.id
        content_type=ContentType.objects.get_for_model(PaymentLink)
        razor_obj=RazorPayPayment.objects.filter(
            object_id=object_id, content_type=content_type.id, captured=True
                ).annotate(
                    # total_sale=Count('id'),
                    total_revenue=Sum('amount')
                )
        razor_obj
        return razor_obj
    


    def get_group_name(self,obj):
        name=obj.group.name
        return name
    


class CustomerlistSerializer(serializers.ModelSerializer):
    product_type=serializers.SerializerMethodField('get_product_type')
    payment_status=serializers.SerializerMethodField('get_payement_status')
    user_status=serializers.SerializerMethodField('get_user_status')
    amount=serializers.SerializerMethodField('get_amount')
    title=serializers.SerializerMethodField('get_title')
    
    class Meta:
        model=Customer
        fields= ['id','title','product_type','amount','user_status','payment_status','email','create_at']




    def get_product_type(self,obj):
        
        content_class = ContentType.objects.get(id=obj.content_type.id)
        model_class =content_class.model_class()
        if model_class==PaymentLink:
            return 'payment'
        elif model_class==TelegramChannelProduct:
            return 'telegram'
        elif model_class==LockMessaging:
            return 'lock_message'
    
    def get_payement_status(self,obj):
        try:
            razor_obj=RazorPayPayment.objects.get(user=obj)
            status=razor_obj.status

            return status
        except Exception as e:
            print(str(e))
            return None
    
    def get_user_status(self,obj):
        return None
    

    def get_amount(self,obj):
        try:
            razor_obj=RazorPayPayment.objects.get(user_id=obj)
            amout=razor_obj.amount
            return amout
        except Exception as e:
            print(str(e))
            return None
    

    def get_title(self,obj):
        content_type=obj.content_type
        content_class = ContentType.objects.get(id=content_type.id)
        model_class =content_class.model_class()
        if model_class==PaymentLink:
            payment_obj=PaymentLink.objects.get(id=obj.object_id)
            return payment_obj.title
        elif model_class==TelegramChannelProduct:
            telegram_obj=TelegramChannelProduct.objects.get(id=obj.object_id)
            return telegram_obj.title
        elif model_class==LockMessaging:
            lock_obj=LockMessaging.objects.get(id=obj.object_id)
            return lock_obj.title
        

    





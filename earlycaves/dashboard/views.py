import logging
from datetime import datetime
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from account.models import User, PaymentLink, LockMessaging
from django.core.paginator import Paginator
from django.db.models import Q, Min


logger = logging.getLogger(__name__)

class AdminDashboard(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.role.lower() == "admin":
            return render(request, "dashboard.html")
        return redirect("admin_login")


class AdminLogin(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info("Username: %s logged in successfully at %s.", username, datetime.now())
            return redirect('admin_dashboard') 
        else:
            messages.error(request, 'Invalid username or password')
            logger.info("Username: %s failed to logged in at %s.", username, datetime.now())
            return render(request, 'login.html')

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('admin_login')
    
    
class PunchInView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'punch_in.html')
    
    def post(self, request, *args, **kwargs):
        # need to implement the functionality 
        pass
    
    
class OnboardingListView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get("q", "")
        queryset = User.objects.filter(role__icontains="client")

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        paginator = Paginator(queryset, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "clients": page_obj.object_list,
            "page_obj": page_obj,
            "search_query": search_query
        }
        return render(request, 'onboarding_list.html', context)

    
    
class PayoutListView(View):
    def get(self, request, *args, **kwargs):
        queryset = PaymentLink.objects.all()
        filter = request.GET.get("filter", None)
        if filter:
            if filter.lower() == "smallest":
                queryset = queryset.order_by("price")
            elif filter.lower() == "largest":
                queryset = queryset.order_by("-price")
            
            elif filter.lower() == "first_payout":
                first_links = (
                        queryset
                        .values('user_id')
                        .annotate(first_created=Min('create_at'))
                    )

                    # Step 2: Build a query to get those specific PaymentLinks
                q = Q()
                for entry in first_links:
                    q |= Q(user_id=entry['user_id'], create_at=entry['first_created'])

                queryset = queryset.filter(q)
            elif filter.lower() == "not_first_payout":
                first_links = (
                        queryset
                        .values('user_id')
                        .annotate(first_created=Min('create_at'))
                    )

                    # Step 2: Build a query to get those specific PaymentLinks
                q = Q()
                for entry in first_links:
                    q |= Q(user_id=entry['user_id'], create_at=entry['first_created'])

                queryset = queryset.exclude(q)
            elif filter.lower() == "earliest_pending":
                queryset = queryset.filter(status="pending")
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

       
        context = {
            "payments":queryset,
            "page_obj": page_obj,
        }
        return render(request, "payout_list.html", context)
    


class ReviewProductView(View):
    def get(self, request, *args, **kwargs):
        queryset = LockMessaging.objects.all()
        filter = request.GET.get("filter", None)
        if filter:
            if filter.lower() == "smallest":
                queryset = queryset.order_by("price")
            elif filter.lower() == "largest":
                queryset = queryset.order_by("-price")
            
            elif filter.lower() == "first_payout":
                first_links = (
                        queryset
                        .values('user_id')
                        .annotate(first_created=Min('create_at'))
                    )

                    # Step 2: Build a query to get those specific PaymentLinks
                q = Q()
                for entry in first_links:
                    q |= Q(user_id=entry['user_id'], create_at=entry['first_created'])

                queryset = queryset.filter(q)
            elif filter.lower() == "not_first_payout":
                first_links = (
                        queryset
                        .values('user_id')
                        .annotate(first_created=Min('create_at'))
                    )

                    # Step 2: Build a query to get those specific PaymentLinks
                q = Q()
                for entry in first_links:
                    q |= Q(user_id=entry['user_id'], create_at=entry['first_created'])

                queryset = queryset.exclude(q)
            elif filter.lower() == "earliest_pending":
                queryset = queryset.filter(status="pending")
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

       
        context = {
            "products":queryset,
            "page_obj": page_obj,
        }
        return render(request, "review_product.html", context)
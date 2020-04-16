from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokenizer import account_activation_token
from .models import *
from .get_plot_data import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login,authenticate,logout
import json
import numpy as np
import datetime as dt
import pandas_datareader.data as web
# Create your views here.

def home(request):
    return render(request,"home.html")

def signup(request):
    if request.method == "POST":
        form = SignUp(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, 'signup.html', {'form': form})
    form = SignUp()
    return render(request, 'signup.html', {'form': form})


def login_(request):
    user_model = get_user_model()
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                user_model.objects.get(email = email)
            except ObjectDoesNotExist:
                form = Login()
                return render(request,"login.html",{"form":form,"errors":"Account doesn't exist"})
            user = authenticate(request,email=email,password=password)
            if not user:
                form = Login()
                return render(request,"login.html",{"form":form,"errors":"Password is incorrect"})

            login(request,user)

            return HttpResponseRedirect(reverse("home"))

        form = Login()
        return render(request,"login.html",{"form":form})

    form = Login()
    return render(request,"login.html",{"form":form})

def logout_(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))

@csrf_exempt
def protfolio(request):
    if str(request.user) is "AnonymousUser" or not request.user.is_active:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        return HttpResponseRedirect(reverse("portfolio"))

    return render(request,"portfolio.html",{"tickers":choice_tickers})

@csrf_exempt
def assets(request):
    if str(request.user) is "AnonymousUser" or not request.user.is_active:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        return HttpResponseRedirect(reverse("asset"))
    try:
        port = Portfolio.objects.get(user = request.user)
        tickers = Ticker.objects.all().filter(portfolio = port)
        return render(request,"analyze_assets.html",{"tickers":choice_tickers,"my_tickers":tickers})
    except ObjectDoesNotExist:
        return render(request,"analyze_assets.html",{"error":"Save a portfolio to view here."})


@csrf_exempt
def add_portfolio(request):
    if request.method=="POST":
        try:
            previous_port = Portfolio.objects.get(user = request.user)
            previous_port.delete()
        except ObjectDoesNotExist:
            pass
        data = json.loads(request.POST["data"])
        name = data["name"]
        portfolio = Portfolio(user = request.user,portfolio_name=name,amount_invested=data["amount_invested"])
        portfolio.save()
        print(portfolio)

        current_ = []
        for name,percent in zip(data["tickers"],data["assets"]):

            ticker = Ticker(ticker_name=name,percentage=float(percent),portfolio=portfolio,description=ticker_dict[name])
            ticker.save()


        return JsonResponse({"ok":"ok"})

@csrf_exempt
def get_plot_data(request):
    if request.method=="POST":
        data = json.loads(request.POST["data"])
        portfolios = np.array(data["portfolios"])/100
        if portfolios.shape[0] == 2:
            start_date = dt.datetime.strptime(data["start_date"], "%Y-%M-%d")
            end_date = dt.datetime.strptime(data["end_date"], "%Y-%M-%d")

            p_return1,p_return2 = get_data(data["tickers"],portfolios,start_date,end_date,float(data["amount_invested"]),portfolios[0],portfolios[1])
            return JsonResponse({"data":[p_return1,p_return2]})
        else:
            start_date = dt.datetime.strptime(data["start_date"], "%Y-%M-%d")
            end_date = dt.datetime.strptime(data["end_date"], "%Y-%M-%d")
            p_return1,p_return2,p_return3 = get_data(data["tickers"],portfolios,start_date,end_date,float(data["amount_invested"]),portfolios[0],portfolios[1],portfolios[2])

            return JsonResponse({"data":[p_return1,p_return2,p_return3]})


@csrf_exempt
def get_share_data(request):
    if request.method=="POST":
        data_ = json.loads(request.POST["data"])
        print()
        data = return_num_shares({"ticker":data_["Your ticker"],"percentage":np.array(data_["Percentage of stocks"])/100,"current":data_["Stock price"]},inv_equity=float(data_["amount_invested"]),)
        return JsonResponse({"data":data})
        # return JsonResponse({"data":data,"port_data":get_data(data_["Your ticker"],[np.array(data_["Percentage of stocks"])/100],"2019-01-01","2020-01-01",10000,np.array(data_["Percentage of stocks"])/100)})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        # User = get_user_model()
        print(User.objects,get_user_model())
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

@csrf_exempt
def get_stock_price(request):
    print(request)
    if request.method == "POST":
        price = get_current_stock_price(request.POST["ticker"])
        return JsonResponse({"price":price})

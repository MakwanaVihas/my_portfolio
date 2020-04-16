from django.db import models
from django.contrib.postgres.fields import FloatRangeField
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.conf import settings
from django.core.validators import MaxValueValidator,MinValueValidator
import pickle
# Create your models here.
ticker_symbol_dict = None
with open(settings.BASE_DIR+"/ticker_symbol_dict.pickle","rb") as f:
    ticker_symbol_dict = pickle.load(f)


choice_symbol_tickers = list(ticker_symbol_dict.items())
ticker_dict = None
with open(settings.BASE_DIR+"/ticker_dict.pickle","rb") as f:
    ticker_dict = pickle.load(f)

choice_tickers = list(ticker_dict.items())


class User(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100,default="")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    email = models.EmailField(unique=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

class Portfolio(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount_invested = models.FloatField(default=0.0)
    portfolio_name = models.CharField(max_length=50,default="My portfolio")

class Ticker(models.Model):
    ticker_name = models.CharField(max_length = 20)
    description = models.CharField(max_length = 300)
    exchange_traded = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0)
    portfolio = models.ForeignKey(Portfolio,on_delete=models.CASCADE)

class AllTickers(models.Model):
    ticker_name = models.CharField(max_length = 10)
    description = models.CharField(max_length = 100)
    exchange = models.CharField(max_length=5)
    etf = models.CharField(max_length=5)

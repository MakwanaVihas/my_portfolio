from django.urls import include,path
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("signup/",views.signup,name="signup"),
    path("login/",views.login_,name="login"),
    path("logout/",views.logout_,name="logout"),
    path("visualize/",views.protfolio,name="portfolio"),
    path("portfolio/",views.assets,name="assets"),

    path("add_portfolio/",views.add_portfolio,name="add_portfolio"),

    path("get_plot_data/",views.get_plot_data,name="plot_data"),
    path("get_stock_price/",views.get_stock_price,name="get_current_stock_price"),

    path("get_share_data/",views.get_share_data,name="get_share"),

    path("activate/<uidb64>/<token>",views.activate,name="activate"),

]

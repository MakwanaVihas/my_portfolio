import datetime as dt
import pandas as pd
import numpy as np
from django.conf import settings
import pandas_datareader.data as web



def get_current_stock_price(ticker):
    one_day = dt.timedelta(days=1)
    stockprice_day = dt.datetime.now()

    one_day_ago = stockprice_day - one_day

    df = web.get_data_yahoo(ticker, one_day_ago, stockprice_day)
    return df["Adj Close"].values[-1]



def portfolio_return(returns,weight1,starting_capital): #returns the return of portfolio with given weights
    equi_por = np.sum(weight1*returns, axis = 1) #weighted gain percentage
    p_return = (equi_por+1).cumprod()*starting_capital #convert into portfolio starting at 10000
    return p_return #Returns a series with date of portfolio value as index, and total portfolio value as column 1


def plot_one_portfolio(returns,weight1,starting_capital):
    p_return1 = portfolio_return(returns,weight1,starting_capital)
    return p_return1

def plot_two_portfolios(returns,weight1,weight2,starting_capital):
    p_return1 = portfolio_return(returns,weight1,starting_capital)
    p_return2 = portfolio_return(returns,weight2,starting_capital)
    return p_return1,p_return2

def plot_three_portfolios(returns,weight1,weight2,weight3,starting_capital): #needs 3 equally long list of weights for 1,2,3
    p_return1 = portfolio_return(returns,weight1,starting_capital)
    p_return2 = portfolio_return(returns,weight2,starting_capital)
    p_return3 = portfolio_return(returns,weight3,starting_capital)

    return p_return1,p_return2,p_return3


def get_data(ticker_name,percentages,start,end,invested,weight1,weight2=None,weight3=None):
    dfa = pd.read_csv(settings.CSV_FOLDER+'/long_tickers_data.csv', parse_dates=True, index_col=0)
    dataframe_list = []
    for i in percentages:
        inp = {"ticker":ticker_name,"percentage":i}

        df = pd.DataFrame(inp)
        # df = df.drop(df.index[df.index[df["percentage"]==0].to_list()])

        dataframe_list.append(df)
        # print(df)

    dfa = dfa.truncate(before=start, after=end)
    dfa = dfa.drop(dfa.columns.difference(dataframe_list[0]['ticker'].values.tolist()), 1, inplace=False)

    table = dfa
    returns = table.pct_change()
    # print(ticker_name,dfa)
    if weight2 is None and weight3 is None:
        p_return1 = []
        p_r1 = plot_one_portfolio(returns,weight1,invested)
        for i in range(len(p_r1)):
            p_return1.append({"x":p_r1.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r1[p_r1.keys()[i]]})
        return p_return1

    if weight3 is None:
        p_return1,p_return2 = [],[]
        p_r1,p_r2 = plot_two_portfolios(returns,weight1,weight2,invested)
        for i in range(len(p_r1)):
            p_return1.append({"x":p_r1.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r1[p_r1.keys()[i]]})
            p_return2.append({"x":p_r2.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r2[p_r2.keys()[i]]})

        return p_return1,p_return2

    else:
        p_return1,p_return2,p_return3 = [],[],[]
        p_r1,p_r2,p_r3 = plot_three_portfolios(returns,weight1,weight2,weight3,invested)
        for i in range(len(p_r1)):

            # p_return1[p_r1.keys()[i].strftime("%Y/%m/%d")] = p_r1[p_r1.keys()[i]]
            # p_return2[p_r2.keys()[i].strftime("%Y/%m/%d")] = p_r2[p_r2.keys()[i]]
            # p_return3[p_r3.keys()[i].strftime("%Y/%m/%d")] = p_r3[p_r3.keys()[i]]

            p_return1.append({"x":p_r1.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r1[p_r1.keys()[i]]})
            p_return2.append({"x":p_r2.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r2[p_r2.keys()[i]]})
            p_return3.append({"x":p_r3.keys()[i].strftime("%Y-%m-%d %H:%M:%S"),"y":p_r3[p_r3.keys()[i]]})
        # print(p_return1)


        return p_return1,p_return2,p_return3




def fill_all_stocks(dfp,stockprice_day,current_price): #gets data from online
    all_stocks = []
    one_day = dt.timedelta(days=1)
    one_day_ago = stockprice_day - one_day

    start1=one_day_ago
    end1=stockprice_day
    for index, row in dfp.iterrows():
        # print(row['ticker'])
        c_stock_price = current_price[index]
        # print(c_stock_price)
        all_stocks.append(c_stock_price)
    dfp['c_stock_price'] = all_stocks
    # print('Stock Prices from '+end1.strftime('%Y-%m-%d'))
    return dfp



def build_data_set(df,inv_equity):
    # Add money allocated:
    df['money_allocated'] = df['percentage']*inv_equity

    #Calcualte number of shares:
    df['num_shares']=np.floor((df['money_allocated'])/(df['c_stock_price']))

    #Calculate money invested in difference from planned:
    df['actual_invested'] =  (df['num_shares'])*(df['c_stock_price'])

    #Calculate difference from invested
    df['difference_from_invested'] = (df['money_allocated']-df['actual_invested'])

    #Calculate  percentage invested of equity we have
    df['percentage_of_equity'] = (df['actual_invested']/inv_equity)

    total_invested = df['actual_invested'].sum(axis = 0, skipna = True)

    #Calculate actual percentage invested
    df['percentage_of_total_invested'] = (df['actual_invested']/total_invested)

    # Calculate difference from invested:
    df['percentage_difference'] = (df['percentage']-df['percentage_of_equity'])
    return df

#Function recalculating percentages if user wants to change his percentages
def recalculate_percentages(df,inv_equity):

    #Calculate money invested in difference from planned:
    df['actual_invested'] =  (df['num_shares'])*(df['c_stock_price'])

    #Calculate difference from invested
    df['difference_from_invested'] = (df['money_allocated']-df['actual_invested'])

    #Calculate  percentage invested of equity we have
    df['percentage_of_equity'] = (df['actual_invested']/inv_equity)

    total_invested = df['actual_invested'].sum(axis = 0, skipna = True)

    #Calculate actual percentage invested
    df['percentage_of_total_invested'] = (df['actual_invested']/total_invested)

    # Calculate difference from invested:
    df['percentage_difference'] = (df['percentage']-df['percentage_of_equity'])
    return df

#Run logical statement to maximise investments (due to round_down)
def adjust_num_shares(df,inv_equity):
    total_invested = df['actual_invested'].sum(axis = 0, skipna = True)
    money_left = inv_equity-total_invested
    index_id = df['percentage_difference'].idxmax(axis=0, skipna=True)

    count1 = 1
    while (total_invested<inv_equity) and (df.at[index_id,'c_stock_price']<(money_left)):
        df.at[index_id,'num_shares']= df.at[index_id,'num_shares']+1
        df = recalculate_percentages(df,inv_equity)
        count1 = count1+1
        index_id = df['percentage_difference'].idxmax(axis=0, skipna=True)
        total_invested = df['actual_invested'].sum(axis = 0, skipna = True)
        money_left = inv_equity-total_invested

    return df

def change_percentage(df,inv_equity,new_percentage):
    percentage_sum = np.sum(new_percentage)

    if percentage_sum != 1: #test that percentage adds to 100
        print("ERROR: Percentage does not add to 100%")
    elif len(new_percentage) != len(df_test.index):
        print("ERROR: not enough elements in list")
    else:
        df['percentage'] = new_percentage
        df = adj_data_set(df,inv_equity)
    return df

def adj_data_set(df,inv_equity):
    df  = adjust_num_shares(build_data_set(df,inv_equity),inv_equity)
    return df

def return_num_shares(data_dict,inv_equity):
    stockprice_day = dt.datetime.now()
    df = pd.DataFrame(data_dict)
    df_1 = fill_all_stocks(df,stockprice_day,data_dict["current"])
    # print(df_1)
    df1 =  adj_data_set(df_1,inv_equity)
    df2 = df1.drop(df1.columns.difference(['ticker','num_shares']), 1, inplace=False)
    return df2.to_dict()

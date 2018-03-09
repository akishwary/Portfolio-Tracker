# -*- coding: utf-8 -*-
"""

The purpose of this class is to create a multiple stock portfolio.

@author: Amrin.Kishwary
"""

#import libraries
import numpy as np #mathematical computation
import pandas as pd #dataframe and data structure
import matplotlib.pyplot as plt #plot and graph
from matplotlib import style #customized plot design
import matplotlib.ticker as mticks #customize tick and ticklables
import matplotlib.dates as mdates #format dates
#import quandl as q #to get stock price data
import aop #cython code pxy file
from Stock import Stock

#key to use quandl 
#q.ApiConfig.api_key = "YourAPIKey"

class Portfolio:
    ''' the class takes in two argument:
        data = transaction data which incl. Ticker, Date, Quantity, and Price
        mkt = which is a dataframe object with stock market price
    '''
    def __init__(self,data,mkt):
         self.data = data
         self.mkt = mkt
         self.stock = {} # dictorary of stocks 
         
         #add stock object for each ticker
         self.add_stock()
         
    #look through transaction and create dictionary of stock objects
    def add_stock(self):
        #create a pandas dataframe object using transaction data 
        trans = self.data
        trans.set_index("Date", inplace=False)
        
        #get the stock tickers 
        tickers= self.data["Ticker"].unique()
        
        #empty list of stocks
        stk = []
        #create stock object for each stock
        for tick in tickers:
            d= get_xlsxData(tick,self.mkt)
            p = trans[(trans["Ticker"]==tick)]
            temp = Stock(tick,p,d)
            stk.append(temp)
        self.stock= dict(zip(tickers,stk))
        
    #get transaction data
    def get_data(self):
        return self.data
    
    #get market price
    def get_mkt(self):
        return self.mkt
    
    #get list of stocks in portfolio
    def get_stock(self):
        tickers = self.stock.keys()
        return sorted(tickers)
    
    #get dictionary of stocks
    def get_dict(self):
        return self.stock
    
    #get unrealized pnl 
    def get_unreal(self):
        df = pd.DataFrame()
        #get dictionary
        d = self.get_dict()
        #get unrealized per stock
        for key, value in d.items():
            df1=value.get_pnl()
            df[key]= df1["Unrealized"]
        #sum all the columns to get total
        df["Unrealized"]=df.sum(axis=1)
        
        return df["Unrealized"];
            
    #get realized pnl 
    def get_real(self):
        df = pd.DataFrame()
        #get dictionary
        d = self.get_dict()
        #get realized per stock
        for key, value in d.items():
            df1=value.get_pnl()
            df[key]= df1["Realized"]
        #sum all the columns to get total
        df["Realized"]=df.sum(axis=1)
        
        return df["Realized"];
       
    #get total pnl 
    def get_total(self):
        df = pd.DataFrame()
        #get dictionary
        d = self.get_dict()
        #get total pnl per stock
        for key, value in d.items():
            df1=value.get_pnl()
            df[key]= df1["Total P&L"]
        #sum all the columns to get total
        df["Total"]=df.sum(axis=1)
        
        return df["Total"];
      
    #get market value
    def get_mkt_value(self):
        df = pd.DataFrame()
        #get dictionary
        d = self.get_dict()
        #get total pnl per stock
        for key, value in d.items():
            df[key]=value.get_mkt_value()
        #sum all the columns to get total
        df["Market Value"]=df.sum(axis=1)
        
        return df["Market Value"];
   
    #get average transaction cost
    def get_ave_tranCost(self):
        df = self.get_data()
        df["Cost"] = df["Quantity"]*df["Price"]
        avg = df["Cost"].mean()
        return avg
    
    #stock with max profits
    def get_maxp(self):
        profit = []
        dic = self.get_dict()
        tick = self.get_stock()
        for i in tick:
            temp = dic.get(i)
            df = temp.get_pnl()
            p = df.iloc[-1]["Total P&L"]
            profit.append((i,p))
        profit.sort(key=lambda x:x[1])
        return profit[-1]
    
    #stock with min profit
    def get_minp(self):
        profit = []
        dic = self.get_dict()
        tick = self.get_stock()
        for i in tick:
            temp = dic.get(i)
            df = temp.get_total_pnl()
            p = df.iloc[-1]["Total P&L"]
            profit.append((i,p))
        profit.sort(key=lambda x:x[1])
        return profit[0]
    
    #returns the $ amount of gain/loss
    def get_pnl(self):
        df = self.get_total()
        return df[-1];
    
    #plot pnl
    def plot_pnl(self):       
        
        style.use("ggplot")
        plt.figure(figsize=(10,7))
        
        #get data
        total_pnl = self.get_total()/1000000
        real_gains=self.get_real()/1000000
        unreal_gains=self.get_unreal()/1000000
        date = total_pnl.index.values
        
        ax1 = plt.subplot2grid((1,1), (0,0), rowspan =1, colspan =1,)
        
        #create subplots 
        ax1.plot_date(date,total_pnl,'-', label="Total", color="#0715FD",
                      linewidth=.7)#totla pnl
        ax1.plot_date(date,real_gains,'--', label="Realized",color='#0715FD',
                      linewidth=.7)#realized pnl
        ax1.plot_date(date,unreal_gains,'-', label="Unrealized",color='#aeabab',
                      linewidth=.7)#unrealized pnl
        
        plt.title("Portfolio PnL",loc='left',color='#8b8b8b',fontsize=20)
        plt.ylabel("PnL (in millions of US$)", color='#636363', labelpad=10)
    
        #changes made to pnl plot(ax1)
        ax1.legend(loc=2, frameon=False,ncol=3)
        ax1.set_facecolor('w')#change background of chart
        ax1.spines["left"].set_color('#8b8b8b')
        #formats y axis ticklabels to include commas
        ax1.get_yaxis().set_major_formatter(mticks.FuncFormatter
                     (lambda x, p:format(int(x), ',')))
        #max number of tickers
        ax1.yaxis.set_major_locator(mticks.MaxNLocator(nbins=7, prune='both'))
        ax1.tick_params(axis='both',labelcolor = '#636363',length=0)
        ax1.axhline(y=0, color='#636363',linewidth=.7)
        ax1.grid(False)
        
        #x axis tick labels for ax1
        ax1.xaxis.set_major_locator(mticks.MaxNLocator(nbins=10))
        ax1.tick_params(axis='both',labelcolor = '#636363',length=0)
        ax1.set_xlim(xmin=date[0])#set x-axis minimum
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        return;
    
    #plot market value
    def plot_mkt_val(self):
        
        style.use("ggplot")
        plt.figure(figsize=(10,7))
        
        #get data
        total_pnl = self.get_total()/1000000
        mkt_val = self.get_mkt_value()/1000000
        date = mkt_val.index.values
        
        ax1 = plt.subplot2grid((1,1), (0,0), rowspan =1, colspan =1,)
        
        #create subplots 
        ax1.plot_date(date,mkt_val,'-', label="Mkt Val",color='#f48020',
                      linewidth=.7)#realized pnl
        ax1.plot_date(date,total_pnl,'-', label="PnL", color="#89898d",
                      linewidth=.7)#totla pnl
        
        plt.title("Portfolio Market Value",loc='left',color='#8b8b8b',fontsize=20)
        plt.ylabel(("in millions of US$"), color='#636363', labelpad=10)
    
        #changes made to pnl plot(ax1)
        ax1.legend(loc=2, frameon=False,ncol=3)
        ax1.set_facecolor('w')#change background of chart
        ax1.spines["left"].set_color('#8b8b8b')
        #formats y axis ticklabels to include commas
        ax1.get_yaxis().set_major_formatter(mticks.FuncFormatter
                     (lambda x, p:format(int(x), ',')))
        #max number of tickers
        ax1.yaxis.set_major_locator(mticks.MaxNLocator(nbins=7, prune='both'))
        ax1.tick_params(axis='both',labelcolor = '#636363',length=0)
        ax1.axhline(y=0, color='#636363',linewidth=.7)
        ax1.grid(False)
        
        #x axis tick labels for ax1
        ax1.xaxis.set_major_locator(mticks.MaxNLocator(nbins=10))
        ax1.tick_params(axis='both',labelcolor = '#636363',length=0)
        ax1.set_xlim(xmin=date[0])#set x-axis minimum
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        return;
        
#to retreive data from quandl 
def get_qdata(ticker,start,end="today"):
    #get market price from quandl
    df = pd.DataFrame()       
    end_day = ""
    if end != "today":
        end_day = end   
    d = q.get("WIKI/"+ticker+".11",start_date = start, end_date=end_day,collapse="daily")
    df["Mkt_Price"]= d["Adj. Close"]
    #drop value for days market was closed
    df= df.dropna(subset=["Mkt_Price"])
    return df;
 
#to retrive data from excel file Bloomberg addin
def get_xlsxData(ticker,data):
    #create a pandas dataframe object using price data
    index = data.index.values
    df= pd.DataFrame(index=index)
    df.index.name = 'Date'
    df["Mkt_Price"]=data[ticker+" US Equity"]
    return df;

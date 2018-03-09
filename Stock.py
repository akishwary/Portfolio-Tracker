"""
@author: Amrin.Kishwary

The purpose of this class is to create a single stock portfolio.

"""
#import libraries
import numpy as np #mathematical computation
import pandas as pd #dataframe and data structure
import matplotlib.pyplot as plt #plot and graph
from matplotlib import style #customized plot design
import matplotlib.ticker as mticks #customize tick and ticklables
import matplotlib.dates as mdates #format dates
import aop #cython code pxy file

class Stock:
    ''' the class takes in three arguments:
        ticker = stritg object 
        transactions = a dataframe object which incls. Date as index, and 2 columns with 
                       header Quantity and Price
        mkt_price = a dataframe object with Date as index and market price of stock
    '''
    def __init__(self, ticker, transactions, mkt_price):
        self.ticker = ticker #stock ticker symbol
        
        self.trans = transactions #as pandas dataframe  
        self.mkt = mkt_price #get market price
    
    #get ticker
    def get_ticker(self):
        return self.ticker;
    
    #get transactions
    def get_transactions(self):
        return self.trans;
    
    #get mkt_price
    def get_mkt_price(self):
        return self.mkt;
    
    #get date 
    def get_date(self):
        df = self.get_mkt_price()
        return df.index.values
    
    #start date 
    def get_start_date(self):
        df = self.get_date()
        return df[0];
    
    #end date
    def get_end_date(self):
        df = self.get_date()
        return df[-1];
    
    #get transaction dates
    def get_transDate(self):
        df = self.get_transactions()
        return df.index.values
    
    #get tranaction cost in dollars
    def get_cost(self):
        df = self.get_transactions()
        df["Cost"]= df["Quantity"]*df["Price"]
        return df["Cost"];
    
    #get pnl of single stock portfolio
    def get_pnl(self, buy_or_sell=True, condition=True, quantity=True, price=True,
                position=True, ave_open=True, mkt_price=True, realized=True, unrealized=True, 
                total=True):
        
        df = self.get_transactions()
        df1 = self.get_mkt_price()
        
        #update positions based on transactions
        df["Position"]= np.cumsum(df["Quantity"])
        
        #set lagged position
        df["Lag Position"] = df["Position"].shift(1)
        df["Lag Position"] = df["Lag Position"].fillna(value=0)
        
        #get trade type: open, increase, partially decrease, reverse or close position
        df["Condition"]=0 
        #open position
        df.loc[(df["Lag Position"]==0),"Condition"]= 1
        #increase position
        df.loc[(np.sign(df["Quantity"])==np.sign(df["Lag Position"])),
                 "Condition"]= 2
        #partially decrease position
        df.loc[(np.sign(df["Position"])==np.sign(df["Lag Position"])) &
                  (np.sign(df["Quantity"])!= np.sign(df["Lag Position"])),
                   "Condition"] = 3
        #reverse position
        df.loc[(np.sign(df["Position"])!=np.sign(df["Lag Position"]))&
                  (df["Lag Position"]!=0),"Condition"]= 4
        #close position
        df.loc[df["Position"]==0, "Condition"]= 5
        
        #calculate average open price
        temp = aop.ave_open_price(df["Condition"].values,df["Quantity"].values,
                           df["Price"].values,df["Lag Position"].values)
        #add to dataframe 
        df["Ave_Open_Price"]=temp
        
        #set tranaction type: buy or sell
        df["Buy/Sell"]=np.where(df["Quantity"]>0,"B","S")
        
        #calculate realized gains
        df["r_gain"]=0.0
        df["q"]=df["Quantity"].abs()
        
        #realized gain when position reverse or partially decrease
        df.loc[(df["Buy/Sell"]=="B") & ((df["Condition"]== 3)|
                (df["Condition"]==4)),"r_gain"]=((df["Ave_Open_Price"].shift(1)-df["Price"])*
                df["q"])
        df.loc[(df["Buy/Sell"]=="S") & ((df["Condition"]== 3)|
                (df["Condition"]==4)),"r_gain"] = ((df["Price"]-df["Ave_Open_Price"].shift(1))*
                df["q"])
        #realized gain when position closes
        df.loc[(df["Buy/Sell"]=="B") & (df["Condition"]== 5),"r_gain"]=(
                 (df["Ave_Open_Price"].shift(1)-df["Price"])*df["q"])
        df.loc[(df["Buy/Sell"]=="S") & (df["Condition"]== 5),"r_gain"]=(
                 (df["Price"]-df["Ave_Open_Price"].shift(1))*df["q"])
        
        #add transactions for price and quanity columns
        df1= df1.join(df, lsuffix="_df1", rsuffix="_df")
        #replace NaN with zeros 
        df1= df1.fillna(value=0)
        
        #update positions 
        df1["Position"]= np.cumsum(df1["Quantity"])
        #update realized gains
        df1["Realized"]=np.cumsum(df1["r_gain"])
        
        #update average open price (cumsum() with reset @ !=0)
        df1["temp"]=0
        df1.loc[df1["Ave_Open_Price"]!=0,"temp"]=1
        df1["temp2"]=df1["temp"].cumsum()
        df1["temp"]=df1.groupby(["temp2"])["Ave_Open_Price"].cumsum()
        df1["Ave_Open_Price"]=df1["temp"]
        
        #drop uncessary columns
        df1=df1.drop(["Lag Position","q","r_gain","temp","temp2"],axis=1)
        #rearrange columns
        df1 = df1[["Buy/Sell","Condition","Quantity","Price", "Position",
                           "Ave_Open_Price","Mkt_Price","Realized"]]
        
        #calculate unrealized gains
        df1["Unrealized"]=(df1["Mkt_Price"]-df1["Ave_Open_Price"])*df1["Position"]
        
        #calculate total p&l
        df1["Total P&L"]=df1["Realized"]+df1["Unrealized"]
        
        #customize and returns data based on needs of the user
        if buy_or_sell==False:
            df1=df1.drop(["Buy/Sell"],axis=1)
        if condition == False:
            df1=df1.drop(["Condition"],axis=1)
        if quantity == False:
            df1=df1.drop(["Quantity"],axis=1)
        if price == False:
            df1=df1.drop(["Price"],axis=1)
        if position == False:
            df1=df1.drop(["Position"],axis=1)
        if ave_open == False:
            df1=df1.drop(["Ave_Open_Price"],axis=1)
        if mkt_price == False:
            df1=df1.drop(["Mkt_Price"],axis=1)
        if realized == False:
            df1=df1.drop(["Realized"],axis=1)
        if unrealized == False:
            df1=df1.drop(["Unrealized"],axis=1)
        if total == False:
            df1=df1.drop(["Total P&L"],axis=1)
            
        return df1;
    
    #get percent change in portfolio
    def get_pct_change(self):
        df= self.get_pnl()
        df1= df["Total P&L"]
        df1= (df1.pct_change())*100
        df1= df1.replace([np.nan, np.inf],0)
        return df1;        
    
    #calculates beta given two series
    @staticmethod 
    def calculate_beta(returns,benchmark):
        #correlateion between returns and benchmark
        corr = returns.corrwith(benchmark)
        #standard deviation of percent change
        pct_returns = (returns.pct_change())
        pct_benchmark = (benchmark.pct_change())
        
        std_returns = pct_returns.std()
        std_benchmark = pct_benchmark()
        
        #formula for beta
        beta = corr*(std_returns/std_benchmark)
        
        return beta;
        
    #get beta of stock
    def get_stock_beta(self,benchmark):
        df = self.get_mkt_price()
        beta = Stock.calculate_beta(df,benchmark)
        return beta
    
    #get beta of returns
    def get_returns_beta(self,benchmark):
        df = self.get_pct_change()
        beta = Stock.calculate_beta(df,benchmark)
        return beta
        
    #get market value 
    def get_mkt_value(self):
        df= self.get_pnl()
        df1 = df["Mkt_Price"]*df["Position"]
        return df1;
    
    #copy pnl to excel file
    def copy_to_excel(self,filename, sheetname,
                buy_or_sell=True, condition=True, quantity=True, price=True,
                position=True, ave_open=True, mkt_price=True, realized=True, unrealized=True, 
                total=True):
        
        df = self.get_pnl(buy_or_sell, condition, quantity, price, position, ave_open,
                          mkt_price, realized, unrealized, total)
        
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer,sheetname)
        writer.save()
      
    #plot running position and p&l
    def plot_stock(self,num=0):
        
        style.use("ggplot")
    
        #get data
        tkr = self.get_ticker()
        date= self.get_date()
        df= self.get_pnl()
        total_pnl = df["Total P&L"]/1000000
        real_gains= df["Realized"]/1000000
        unreal_gains= df["Unrealized"]/1000000
        position= df["Position"]/1000
        
        plt.figure(figsize=(10,7))
        
        #create subplots 
        ax1 = plt.subplot2grid((6,1), (0,0), rowspan =5, colspan =1,)
        plt.title(tkr.upper(),loc='left',color='#8b8b8b',fontsize=20)
        plt.ylabel("PnL (in millions of US$)", color='#636363', labelpad=10)
        ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
        plt.ylabel("Position" , color='#636363', labelpad=10)
        
        #changes made to pnl plot(ax1)
        ax1.plot_date(date,total_pnl,'-', label="Total", color="#0715FD",
                      linewidth=.7)#totla pnl
        ax1.plot_date(date,real_gains,'--', label="Realized",color='#0715FD',
                      linewidth=.7)#realized pnl
        ax1.plot_date(date,unreal_gains,'-', label="Unrealized",color='#aeabab',
                      linewidth=.7)#unrealized pnl
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
        
        #changes made to position plot(ax2)
        ax2.plot_date(date, position, '-', color='w',linewidth='.01')
        ax2.set_facecolor('w')
        ax2.spines["left"].set_color('#8b8b8b')
        ax2.fill_between(date,0,position, facecolor='#aeabab')
        #format date 
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
        ax2.set_xlim(xmin=date[0])#set x-axis minimum
        ax2.get_yaxis().set_major_formatter(mticks.FuncFormatter
                     (lambda x, p:'{0}K'.format(int(x))))
        ax2.xaxis.set_major_locator(mticks.MaxNLocator(nbins=10))
        ax2.yaxis.set_major_locator(mticks.MaxNLocator(nbins=5,prune='upper'))
        ax2.tick_params(axis='both',labelcolor = '#636363',length=0)
        ax2.grid(False)
        
        #hide x axis tick labels for ax1
        plt.setp(ax1.get_xticklabels(),visible=False)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        return;

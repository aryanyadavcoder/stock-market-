import yfinance as yf
import Sharefunctions as sn
import matplotlib.pyplot as plt

while True:
    print("<---menu--->")
    print("0-Exit,1-Buy,2-Sell,3-View current price,4-chart,5-Show Buy data")
    option = int(input("Enter option\n"))
    if option == 0:
        print("Exit")
        exit()
    elif option == 1:
        sn.buystock()
    
    elif option == 2:
        print("Sell")
        continue
    
    elif option == 3:
        print("<---Menu--->")
        print("1-RELIANCE,2-TCS,3-ITC,4-MRF")
        n = int(input("Enter number\n"))
        
        if n==1:
            stock = "RELIANCE.NS"
        elif n==2:
            stock = "TCS.NS"
        elif n==3:
            stock = "ITC.NS"
        elif n==4:
            stock = "MRF.NS"            
        
        data = yf.download(stock, period="1d", interval="1m")
        print(data)
        continue
    elif option == 4:
        print("Chart")
        print("<---Menu--->")
        print("1-RELIANCE,2-TCS,3-ITC,4-MRF")
        n = int(input("Enter number\n"))
        
        if n==1:
            stock = "RELIANCE.NS"
        elif n==2:
            stock = "TCS.NS"
        elif n==3:
            stock = "ITC.NS"
        elif n==4:
            stock = "MRF.NS"            
        start = input("Enter start date :")
        end = input("Enter end date :")
        data = yf.download(stock, start, end)
        sn.plotgraph(data,stock)
        continue
    elif option == 5:
        sn.showBuydata()
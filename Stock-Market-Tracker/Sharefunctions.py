
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import json


def downloadData(sharename):
    data = yf.download(sharename, start="2025-12-9", end="2026-03-10")

    data.to_csv(f"{sharename}.csv")
    return data


def readCSV(sharename):
    df = pd.read_csv(f"{sharename}.csv")
    return df


def readPrice(sharename):
    csv = readCSV(sharename)
    prices = csv["Close"].iloc[-1]
    return prices


def plotgraph(data, sharename):
    plt.plot(data["Open"], linestyle="--")
    plt.plot(data["Close"], linestyle="--")

    plt.title(sharename)
    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend(["Open", "Close"])
    plt.show()


def buystock():

    print("<---Menu--->")
    print("1-RELIANCE,2-TCS,3-ITC,4-MRF")
    sharename = int(input("Enter the Stock number\n"))

    if sharename == 1:
            stock = "RELIANCE.NS"
    elif  sharename==2:
            stock = "TCS.NS"
    elif sharename==3:
            stock = "ITC.NS"
    elif sharename==4:
            stock = "MRF.NS"  
    
    quantity = int(input("Enter the quantity :"))
    Buy_price = int(input("Enter the Buy price :"))
    stock = {
        "name": stock,
        "quantity": quantity,
        "buy_price": Buy_price
    }

    with open("Buy_data.json", "w") as f:
        json.dump(stock, f, indent=4)

    print("Stock saved to Buy_data")
    
    
def showBuydata():

    with open("Buy_data.json") as f:

        data = json.load(f)

    print(data)    


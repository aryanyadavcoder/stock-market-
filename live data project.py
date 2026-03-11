# Download and save


import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


def downloadData(sharename):
    data = yf.download(sharename, start="2025-12-9", end="2026-03-10")

# Save to CSV
    data.to_csv(f"{sharename}.csv")
    return data


def readCSV(sharename):
    df = pd.read_csv(f"{sharename}.csv")
    return df


def readPrice(sharename):
    csv = readCSV(sharename)
    prices = csv["Close"][2]
    return prices


def plotgraph(data, sharename):
    plt.plot(data["Open"], linestyle="--")
    plt.plot(data["Close"], linestyle="--")

    plt.title(sharename)
    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend(["Open", "Close"])
    plt.show()


print("--menu--")
print("0-exit,1-RELIANCE.NS,2-ITC.NS,3-TCS.NS")
shares = ["RELIANCE.NS", "ITC.NS", "TCS.NS"]

n = int(input("Enter the number :"))
if n == 0:
    print("Exit")
    exit()

# Download data
# data = yf.download(shares[n-1], start="2024-01-01", end="2026-02-20")
data = downloadData(shares[n-1])
print(data)
# g=readCSV(shares[n-1])
prices = readPrice(shares[n-1])
print(prices)
plotgraph(data, shares[n-1])

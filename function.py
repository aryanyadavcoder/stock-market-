import os
import re
import json
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def _ensure_dir(folder: str) -> None:
    os.makedirs(folder, exist_ok=True)


def _json_default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type not serializable: {type(obj)}")


def _save_json(data, file_path: str) -> None:
    _ensure_dir(os.path.dirname(file_path) or ".")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=_json_default)


def _load_json(file_path: str, default_value):
    if not os.path.exists(file_path):
        return default_value
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    return df


def _add_extra_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Close" in df.columns:
        df["Daily Return %"] = df["Close"].pct_change() * 100
    if {"High", "Low"}.issubset(df.columns):
        df["High-Low Gap"] = df["High"] - df["Low"]
    if {"Open", "Close"}.issubset(df.columns):
        df["Open-Close Change"] = df["Close"] - df["Open"]
    return df


def _download_share_data(share_name: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(
        share_name,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )
    if df.empty:
        raise ValueError(f"No data found for {share_name}. Check the ticker symbol.")
    df = _flatten_columns(df)
    df = df.dropna(how="all").copy()
    df = _add_extra_columns(df)
    return df


def _calculate_statistics(series: pd.Series, column_name: str, share_name: str) -> dict:
    x = series.dropna().to_numpy(dtype=float)

    if len(x) == 0:
        return {
            "Share": share_name,
            "Column": column_name,
            "Count": 0,
            "Sum": None,
            "Mean": None,
            "Median": None,
            "Mode": [],
            "Min": None,
            "Q1": None,
            "Q2": None,
            "Q3": None,
            "IQR": None,
            "Max": None,
            "Range": None,
            "Variance (Population)": None,
            "Std Dev (Population)": None,
            "Variance (Sample)": None,
            "Std Dev (Sample)": None,
            "Skewness": None,
            "Kurtosis": None,
        }

    values, counts = np.unique(x, return_counts=True)
    max_count = np.max(counts)
    modes = values[counts == max_count].tolist()

    q1 = np.percentile(x, 25)
    q2 = np.percentile(x, 50)
    q3 = np.percentile(x, 75)

    sample_variance = np.var(x, ddof=1) if len(x) > 1 else np.nan
    sample_std = np.std(x, ddof=1) if len(x) > 1 else np.nan

    return {
        "Share": share_name,
        "Column": column_name,
        "Count": int(len(x)),
        "Sum": float(np.sum(x)),
        "Mean": float(np.mean(x)),
        "Median": float(np.median(x)),
        "Mode": modes,
        "Min": float(np.min(x)),
        "Q1": float(q1),
        "Q2": float(q2),
        "Q3": float(q3),
        "IQR": float(q3 - q1),
        "Max": float(np.max(x)),
        "Range": float(np.max(x) - np.min(x)),
        "Variance (Population)": float(np.var(x)),
        "Std Dev (Population)": float(np.std(x)),
        "Variance (Sample)": float(sample_variance) if not np.isnan(sample_variance) else None,
        "Std Dev (Sample)": float(sample_std) if not np.isnan(sample_std) else None,
        "Skewness": float(pd.Series(x).skew()) if len(x) > 2 else None,
        "Kurtosis": float(pd.Series(x).kurt()) if len(x) > 3 else None,
    }


def _collect_stats(df: pd.DataFrame, share_name: str) -> pd.DataFrame:
    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    rows = [_calculate_statistics(df[col], col, share_name) for col in numeric_columns]
    return pd.DataFrame(rows)


def _save_line_chart(x, y, title, xlabel, ylabel, file_path):
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(file_path, dpi=150, bbox_inches="tight")
    plt.close()


def _save_single_share_charts(df: pd.DataFrame, share_name: str, prefix: str, output_dir: str) -> list:
    chart_files = []
    if "Close" in df.columns:
        file_path = os.path.join(output_dir, f"{prefix}_close_line.png")
        _save_line_chart(df.index, df["Close"], f"{share_name} Closing Price", "Date", "Close Price", file_path)
        chart_files.append(file_path)

    if "Volume" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df["Volume"])
        plt.title(f"{share_name} Volume")
        plt.xlabel("Date")
        plt.ylabel("Volume")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_volume_bar.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(file_path)

    if "Close" in df.columns:
        plt.figure(figsize=(8, 5))
        plt.hist(df["Close"].dropna(), bins=10)
        plt.title(f"{share_name} Close Price Histogram")
        plt.xlabel("Close Price")
        plt.ylabel("Frequency")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_histogram.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(file_path)

    if "Daily Return %" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["Daily Return %"], marker="o")
        plt.axhline(0, linewidth=1)
        plt.title(f"{share_name} Daily Return %")
        plt.xlabel("Date")
        plt.ylabel("Return %")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_daily_return_line.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(file_path)

    if {"Open", "High", "Low", "Close"}.issubset(df.columns):
        plt.figure(figsize=(8, 5))
        plt.boxplot(
            [df[c].dropna() for c in ["Open", "High", "Low", "Close"]],
            tick_labels=["Open", "High", "Low", "Close"],
        )
        plt.title(f"{share_name} OHLC Box Plot")
        plt.ylabel("Price")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_ohlc_boxplot.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(file_path)

    return chart_files


def analyze_share(share_name: str, period: str = "1mo", interval: str = "1d", output_dir: str = "stock_output"):
    _ensure_dir(output_dir)
    safe_name = _sanitize_name(share_name)
    prefix = f"{safe_name}_{period}_{interval}"

    df = _download_share_data(share_name, period, interval)

    raw_csv = os.path.join(output_dir, f"{prefix}_raw_data.csv")
    raw_json = os.path.join(output_dir, f"{prefix}_raw_data.json")
    stats_csv = os.path.join(output_dir, f"{prefix}_statistics.csv")
    stats_json = os.path.join(output_dir, f"{prefix}_statistics.json")

    df.to_csv(raw_csv)
    _save_json(df.reset_index().to_dict(orient="records"), raw_json)

    stats_df = _collect_stats(df, share_name)
    stats_df.to_csv(stats_csv, index=False)
    _save_json(stats_df.to_dict(orient="records"), stats_json)

    chart_files = _save_single_share_charts(df, share_name, prefix, output_dir)

    return {
        "share": share_name,
        "data": df,
        "statistics": stats_df,
        "raw_csv": raw_csv,
        "raw_json": raw_json,
        "stats_csv": stats_csv,
        "stats_json": stats_json,
        "chart_files": chart_files,
    }


def analyze_two_shares(share1: str, share2: str, period: str = "1mo", interval: str = "1d", output_dir: str = "stock_compare_output"):
    _ensure_dir(output_dir)
    safe_share1 = _sanitize_name(share1)
    safe_share2 = _sanitize_name(share2)
    prefix = f"{safe_share1}_vs_{safe_share2}_{period}_{interval}"

    df1 = _download_share_data(share1, period, interval)
    df2 = _download_share_data(share2, period, interval)

    raw1_csv = os.path.join(output_dir, f"{safe_share1}_{period}_{interval}_raw.csv")
    raw2_csv = os.path.join(output_dir, f"{safe_share2}_{period}_{interval}_raw.csv")
    raw1_json = os.path.join(output_dir, f"{safe_share1}_{period}_{interval}_raw.json")
    raw2_json = os.path.join(output_dir, f"{safe_share2}_{period}_{interval}_raw.json")

    df1.to_csv(raw1_csv)
    df2.to_csv(raw2_csv)
    _save_json(df1.reset_index().to_dict(orient="records"), raw1_json)
    _save_json(df2.reset_index().to_dict(orient="records"), raw2_json)

    stats1 = _collect_stats(df1, share1)
    stats2 = _collect_stats(df2, share2)
    all_stats = pd.concat([stats1, stats2], ignore_index=True)

    stats_csv = os.path.join(output_dir, f"{prefix}_statistics.csv")
    stats_json = os.path.join(output_dir, f"{prefix}_statistics.json")
    all_stats.to_csv(stats_csv, index=False)
    _save_json(all_stats.to_dict(orient="records"), stats_json)

    comparison_rows = []
    for col_name in ["Close", "Volume", "Daily Return %", "High-Low Gap", "Open-Close Change"]:
        if col_name in df1.columns and col_name in df2.columns:
            row1 = stats1[stats1["Column"] == col_name].iloc[0]
            row2 = stats2[stats2["Column"] == col_name].iloc[0]
            comparison_rows.append({
                "Column": col_name,
                f"{share1} Mean": row1["Mean"],
                f"{share2} Mean": row2["Mean"],
                f"{share1} Std Dev": row1["Std Dev (Population)"],
                f"{share2} Std Dev": row2["Std Dev (Population)"],
                f"{share1} Min": row1["Min"],
                f"{share2} Min": row2["Min"],
                f"{share1} Max": row1["Max"],
                f"{share2} Max": row2["Max"],
            })

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_csv = os.path.join(output_dir, f"{prefix}_comparison_summary.csv")
    comparison_json = os.path.join(output_dir, f"{prefix}_comparison_summary.json")
    comparison_df.to_csv(comparison_csv, index=False)
    _save_json(comparison_df.to_dict(orient="records"), comparison_json)

    common_index = df1.index.intersection(df2.index)
    aligned1 = df1.loc[common_index].copy()
    aligned2 = df2.loc[common_index].copy()

    chart_files = []

    if "Close" in aligned1.columns and "Close" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["Close"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["Close"], marker="o", label=share2)
        plt.title(f"{share1} vs {share2} Close Price")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        p = os.path.join(output_dir, f"{prefix}_close_comparison.png")
        plt.savefig(p, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(p)

        norm1 = aligned1["Close"] / aligned1["Close"].iloc[0] * 100
        norm2 = aligned2["Close"] / aligned2["Close"].iloc[0] * 100
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, norm1, marker="o", label=share1)
        plt.plot(aligned2.index, norm2, marker="o", label=share2)
        plt.title(f"{share1} vs {share2} Normalized Performance")
        plt.xlabel("Date")
        plt.ylabel("Base = 100")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        p = os.path.join(output_dir, f"{prefix}_normalized_close.png")
        plt.savefig(p, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(p)

    if "Daily Return %" in aligned1.columns and "Daily Return %" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["Daily Return %"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["Daily Return %"], marker="o", label=share2)
        plt.axhline(0, linewidth=1)
        plt.title(f"{share1} vs {share2} Daily Return %")
        plt.xlabel("Date")
        plt.ylabel("Return %")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        p = os.path.join(output_dir, f"{prefix}_daily_return_comparison.png")
        plt.savefig(p, dpi=150, bbox_inches="tight")
        plt.close()
        chart_files.append(p)

    return {
        share1: {"data": df1, "raw_csv": raw1_csv, "raw_json": raw1_json, "stats": stats1},
        share2: {"data": df2, "raw_csv": raw2_csv, "raw_json": raw2_json, "stats": stats2},
        "all_statistics": all_stats,
        "statistics_csv": stats_csv,
        "statistics_json": stats_json,
        "comparison_summary": comparison_df,
        "comparison_csv": comparison_csv,
        "comparison_json": comparison_json,
        "chart_files": chart_files,
    }


class DemoTradingApp:
    def __init__(self, data_dir: str = "demo_trading_data"):
        self.data_dir = data_dir
        _ensure_dir(self.data_dir)
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")
        self.snapshots_dir = os.path.join(self.data_dir, "market_snapshots")
        _ensure_dir(self.snapshots_dir)
        self.users = _load_json(self.users_file, {})
        self.transactions = _load_json(self.transactions_file, [])

    def _save_state(self):
        _save_json(self.users, self.users_file)
        _save_json(self.transactions, self.transactions_file)

    def create_user(self, username: str, starting_cash: float = 100000.0):
        if not username.strip():
            raise ValueError("Username cannot be empty.")
        if username in self.users:
            raise ValueError("User already exists.")
        self.users[username] = {
            "cash": float(starting_cash),
            "portfolio": {},
            "created_at": datetime.now().isoformat()
        }
        self._save_state()
        return self.users[username]

    def _require_user(self, username: str):
        if username not in self.users:
            raise ValueError("User not found. Create the user first.")

    def deposit_cash(self, username: str, amount: float):
        self._require_user(username)
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.users[username]["cash"] += float(amount)
        txn = {"type": "deposit", "username": username, "amount": float(amount), "timestamp": datetime.now().isoformat()}
        self.transactions.append(txn)
        self._save_state()
        return txn

    def get_latest_price(self, ticker: str) -> float:
        df = _download_share_data(ticker, period="5d", interval="1d")
        return float(df["Close"].dropna().iloc[-1])

    def buy_share(self, username: str, ticker: str, quantity: int):
        self._require_user(username)
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        price = self.get_latest_price(ticker)
        total_cost = price * quantity
        if self.users[username]["cash"] < total_cost:
            raise ValueError("Not enough cash.")

        portfolio = self.users[username]["portfolio"]
        if ticker not in portfolio:
            portfolio[ticker] = {"quantity": 0, "avg_buy_price": 0.0}

        old_qty = portfolio[ticker]["quantity"]
        old_avg = portfolio[ticker]["avg_buy_price"]
        new_qty = old_qty + quantity
        new_avg = ((old_qty * old_avg) + (quantity * price)) / new_qty

        portfolio[ticker]["quantity"] = int(new_qty)
        portfolio[ticker]["avg_buy_price"] = float(new_avg)
        self.users[username]["cash"] -= total_cost

        txn = {"type": "buy", "username": username, "ticker": ticker, "quantity": int(quantity), "price": float(price), "total": float(total_cost), "timestamp": datetime.now().isoformat()}
        self.transactions.append(txn)
        self._save_state()
        return txn

    def sell_share(self, username: str, ticker: str, quantity: int):
        self._require_user(username)
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        portfolio = self.users[username]["portfolio"]
        if ticker not in portfolio or portfolio[ticker]["quantity"] < quantity:
            raise ValueError("Not enough shares to sell.")

        price = self.get_latest_price(ticker)
        total_value = price * quantity

        portfolio[ticker]["quantity"] -= quantity
        if portfolio[ticker]["quantity"] == 0:
            del portfolio[ticker]

        self.users[username]["cash"] += total_value

        txn = {"type": "sell", "username": username, "ticker": ticker, "quantity": int(quantity), "price": float(price), "total": float(total_value), "timestamp": datetime.now().isoformat()}
        self.transactions.append(txn)
        self._save_state()
        return txn

    def get_user_transactions(self, username: str) -> list:
        self._require_user(username)
        txns = [t for t in self.transactions if t.get("username") == username]
        txns_file = os.path.join(self.data_dir, f"{_sanitize_name(username)}_transactions.json")
        _save_json(txns, txns_file)
        return txns

    def get_portfolio_report(self, username: str) -> dict:
        self._require_user(username)
        user = self.users[username]
        cash = float(user["cash"])
        portfolio = user["portfolio"]

        holdings = []
        total_market_value = 0.0
        total_cost_value = 0.0

        for ticker, item in portfolio.items():
            qty = int(item["quantity"])
            avg_buy_price = float(item["avg_buy_price"])
            current_price = self.get_latest_price(ticker)

            cost_value = qty * avg_buy_price
            market_value = qty * current_price
            pnl = market_value - cost_value

            total_market_value += market_value
            total_cost_value += cost_value

            holdings.append({
                "ticker": ticker,
                "quantity": qty,
                "avg_buy_price": avg_buy_price,
                "current_price": current_price,
                "cost_value": cost_value,
                "market_value": market_value,
                "pnl": pnl
            })

        total_value = cash + total_market_value
        total_pnl = total_market_value - total_cost_value

        report = {
            "username": username,
            "cash": cash,
            "holdings": holdings,
            "total_market_value": total_market_value,
            "total_portfolio_value": total_value,
            "total_pnl": total_pnl,
            "generated_at": datetime.now().isoformat()
        }
        report_file = os.path.join(self.data_dir, f"{_sanitize_name(username)}_portfolio_report.json")
        _save_json(report, report_file)
        return report

    def save_market_snapshot(self, ticker: str, period: str = "1mo", interval: str = "1d"):
        return analyze_share(ticker, period=period, interval=interval, output_dir=self.snapshots_dir)
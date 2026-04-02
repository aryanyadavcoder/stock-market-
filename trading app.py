import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from function import analyze_share, analyze_two_shares, DemoTradingApp


class StockTradingGUI:  
    def __init__(self, root):
        self.root = root
        self.root.title("PP   Tkinter Stock Trading GUI")
        self.root.geometry("1360x860")
        self.root.minsize(1180, 760)

        self.colors = {
            "bg": "#fff8eb",
            "panel": "#ffffff",
            "panel2": "#fff3da",
            "ink": "#1f2937",
            "muted": "#6b7280",
            "brand": "#d97706",
            "brand2": "#f59e0b",
            "line": "#eed7a5",
        }

        self.root.configure(bg=self.colors["bg"])
        self.trading = DemoTradingApp()
        self.current_analysis_result = None
        self.current_comparison_result = None

        self._configure_style()
        self._build_layout()
        self.refresh_user_combo()

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.colors["brand2"])])
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background=self.colors["brand"], foreground="white", padding=8, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", self.colors["brand2"])])
        style.configure("Soft.TButton", padding=8, font=("Segoe UI", 10))

    def _build_layout(self):
        header = tk.Frame(self.root, bg=self.colors["brand"], height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="PP   Tkinter Stock Trading GUI", bg=self.colors["brand"], fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=18)
        tk.Label(header, text="Analysis • Comparison • Demo Trading • Table View • Chart Preview",
                 bg=self.colors["brand"], fg="#fff5e6", font=("Segoe UI", 10)).pack(side="left", padx=8, pady=6)

        body = tk.Frame(self.root, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=12)

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True)

        self.tab_analyze = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.tab_compare = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.tab_trade = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.tab_log = tk.Frame(self.notebook, bg=self.colors["bg"])

        self.notebook.add(self.tab_analyze, text="Analyze One")
        self.notebook.add(self.tab_compare, text="Compare Two")
        self.notebook.add(self.tab_trade, text="Demo Trading")
        self.notebook.add(self.tab_log, text="Log")

        self._build_analyze_tab()
        self._build_compare_tab()
        self._build_trade_tab()
        self._build_log_tab()

    def _section(self, parent, title):
        outer = tk.Frame(parent, bg=self.colors["bg"])
        card = tk.Frame(outer, bg=self.colors["panel"], highlightbackground=self.colors["line"], highlightthickness=1)
        card.pack(fill="both", expand=True)
        head = tk.Frame(card, bg=self.colors["panel2"], height=44)
        head.pack(fill="x")
        head.pack_propagate(False)
        tk.Label(head, text=title, bg=self.colors["panel2"], fg=self.colors["ink"], font=("Segoe UI", 11, "bold")).pack(side="left", padx=12)
        content = tk.Frame(card, bg=self.colors["panel"])
        content.pack(fill="both", expand=True, padx=12, pady=12)
        return outer, content

    def _labeled_entry(self, parent, label, variable, row, width=22):
        tk.Label(parent, text=label, bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=row, column=0, sticky="w", pady=6)
        tk.Entry(parent, textvariable=variable, width=width, relief="solid", bd=1).grid(row=row, column=1, sticky="w", pady=6, padx=(8, 0))

    def _build_treeview(self, parent, columns):
        frame = tk.Frame(parent, bg=self.colors["panel"])
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        y.grid(row=0, column=1, sticky="ns")
        x.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return frame, tree

    def _build_analyze_tab(self):
        top = tk.Frame(self.tab_analyze, bg=self.colors["bg"])
        top.pack(fill="x", padx=8, pady=8)

        left_wrap, form = self._section(top, "Inputs")
        left_wrap.pack(side="left", fill="y", padx=(0, 8))

        self.single_ticker = tk.StringVar(value="RELIANCE.NS")
        self.single_period = tk.StringVar(value="1mo")
        self.single_interval = tk.StringVar(value="1d")
        self.single_output = tk.StringVar(value="stock_output")

        self._labeled_entry(form, "Ticker", self.single_ticker, 0)
        self._labeled_entry(form, "Period", self.single_period, 1)
        self._labeled_entry(form, "Interval", self.single_interval, 2)
        self._labeled_entry(form, "Output Folder", self.single_output, 3, width=30)

        btnrow = tk.Frame(form, bg=self.colors["panel"])
        btnrow.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(btnrow, text="Browse", command=self._browse_single_output, style="Soft.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow, text="Analyze Share", command=self.run_single_analysis, style="Accent.TButton").pack(side="left")

        right = tk.Frame(top, bg=self.colors["bg"])
        right.pack(side="left", fill="both", expand=True)
        preview_wrap, preview_content = self._section(right, "Chart Preview")
        preview_wrap.pack(fill="both", expand=True)

        self.single_chart_choice = tk.StringVar(value="")
        select_row = tk.Frame(preview_content, bg=self.colors["panel"])
        select_row.pack(fill="x", pady=(0, 8))
        tk.Label(select_row, text="Chart:", bg=self.colors["panel"], fg=self.colors["ink"]).pack(side="left")
        self.single_chart_combo = ttk.Combobox(select_row, textvariable=self.single_chart_choice, width=36, state="readonly")
        self.single_chart_combo.pack(side="left", padx=8)
        self.single_chart_combo.bind("<<ComboboxSelected>>", lambda e: self.update_single_chart())

        self.single_fig = Figure(figsize=(7.2, 4.4), dpi=100)
        self.single_ax = self.single_fig.add_subplot(111)
        self.single_canvas = FigureCanvasTkAgg(self.single_fig, master=preview_content)
        self.single_canvas.get_tk_widget().pack(fill="both", expand=True)

        bottom = tk.Frame(self.tab_analyze, bg=self.colors["bg"])
        bottom.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        stats_wrap, stats_content = self._section(bottom, "Statistics Table")
        stats_wrap.pack(fill="both", expand=True)
        self.single_stats_frame, self.single_stats_tree = self._build_treeview(
            stats_content,
            columns=("Column", "Count", "Mean", "Median", "Min", "Q1", "Q2", "Q3", "Max", "StdDev"),
        )
        self.single_stats_frame.pack(fill="both", expand=True)

    def _build_compare_tab(self):
        top = tk.Frame(self.tab_compare, bg=self.colors["bg"])
        top.pack(fill="x", padx=8, pady=8)

        left_wrap, form = self._section(top, "Inputs")
        left_wrap.pack(side="left", fill="y", padx=(0, 8))

        self.compare_ticker1 = tk.StringVar(value="RELIANCE.NS")
        self.compare_ticker2 = tk.StringVar(value="TCS.NS")
        self.compare_period = tk.StringVar(value="1mo")
        self.compare_interval = tk.StringVar(value="1d")
        self.compare_output = tk.StringVar(value="stock_compare_output")

        self._labeled_entry(form, "Ticker 1", self.compare_ticker1, 0)
        self._labeled_entry(form, "Ticker 2", self.compare_ticker2, 1)
        self._labeled_entry(form, "Period", self.compare_period, 2)
        self._labeled_entry(form, "Interval", self.compare_interval, 3)
        self._labeled_entry(form, "Output Folder", self.compare_output, 4, width=30)

        btnrow = tk.Frame(form, bg=self.colors["panel"])
        btnrow.grid(row=5, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(btnrow, text="Browse", command=self._browse_compare_output, style="Soft.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow, text="Compare Shares", command=self.run_comparison, style="Accent.TButton").pack(side="left")

        right = tk.Frame(top, bg=self.colors["bg"])
        right.pack(side="left", fill="both", expand=True)
        preview_wrap, preview_content = self._section(right, "Comparison Chart Preview")
        preview_wrap.pack(fill="both", expand=True)

        self.compare_chart_choice = tk.StringVar(value="")
        row = tk.Frame(preview_content, bg=self.colors["panel"])
        row.pack(fill="x", pady=(0, 8))
        tk.Label(row, text="Chart:", bg=self.colors["panel"], fg=self.colors["ink"]).pack(side="left")
        self.compare_chart_combo = ttk.Combobox(row, textvariable=self.compare_chart_choice, width=36, state="readonly")
        self.compare_chart_combo.pack(side="left", padx=8)
        self.compare_chart_combo.bind("<<ComboboxSelected>>", lambda e: self.update_compare_chart())

        self.compare_fig = Figure(figsize=(7.2, 4.4), dpi=100)
        self.compare_ax = self.compare_fig.add_subplot(111)
        self.compare_canvas = FigureCanvasTkAgg(self.compare_fig, master=preview_content)
        self.compare_canvas.get_tk_widget().pack(fill="both", expand=True)

        bottom = tk.Frame(self.tab_compare, bg=self.colors["bg"])
        bottom.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        compare_wrap, compare_content = self._section(bottom, "Comparison Summary")
        compare_wrap.pack(fill="both", expand=True)
        self.compare_frame, self.compare_tree = self._build_treeview(
            compare_content,
            columns=("Column", "Mean1", "Mean2", "Std1", "Std2", "Min1", "Min2", "Max1", "Max2"),
        )
        self.compare_frame.pack(fill="both", expand=True)

    def _summary_card(self, parent, title, var, r, c):
        card = tk.Frame(parent, bg=self.colors["panel2"], highlightbackground=self.colors["line"], highlightthickness=1, padx=14, pady=12)
        card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
        parent.grid_columnconfigure(c, weight=1)
        parent.grid_rowconfigure(r, weight=1)
        tk.Label(card, text=title, bg=self.colors["panel2"], fg=self.colors["muted"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(card, textvariable=var, bg=self.colors["panel2"], fg=self.colors["ink"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(6, 0))

    def _build_trade_tab(self):
        top = tk.Frame(self.tab_trade, bg=self.colors["bg"])
        top.pack(fill="x", padx=8, pady=8)

        left_wrap, user_content = self._section(top, "User & Trading Controls")
        left_wrap.pack(side="left", fill="y", padx=(0, 8))

        self.trade_user = tk.StringVar()
        self.trade_cash = tk.StringVar(value="100000")
        self.trade_ticker = tk.StringVar(value="RELIANCE.NS")
        self.trade_qty = tk.StringVar(value="1")
        
        # --- ADDED: Auto-Trade Variables ---
        self.trade_target_price = tk.StringVar(value="0.00")
        self.auto_trade_active = tk.BooleanVar(value=False)

        tk.Label(user_content, text="User", bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=0, column=0, sticky="w", pady=6)
        self.user_combo = ttk.Combobox(user_content, textvariable=self.trade_user, width=26)
        self.user_combo.grid(row=0, column=1, sticky="w", pady=6)

        tk.Label(user_content, text="Starting Cash / Deposit", bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=1, column=0, sticky="w", pady=6)
        tk.Entry(user_content, textvariable=self.trade_cash, width=28, relief="solid", bd=1).grid(row=1, column=1, sticky="w", pady=6)

        tk.Label(user_content, text="Ticker", bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=2, column=0, sticky="w", pady=6)
        tk.Entry(user_content, textvariable=self.trade_ticker, width=28, relief="solid", bd=1).grid(row=2, column=1, sticky="w", pady=6)

        tk.Label(user_content, text="Quantity", bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=3, column=0, sticky="w", pady=6)
        tk.Entry(user_content, textvariable=self.trade_qty, width=28, relief="solid", bd=1).grid(row=3, column=1, sticky="w", pady=6)

        # --- ADDED: Target Price & Checkbutton UI ---
        tk.Label(user_content, text="Target Price", bg=self.colors["panel"], fg=self.colors["ink"]).grid(row=4, column=0, sticky="w", pady=6)
        tk.Entry(user_content, textvariable=self.trade_target_price, width=28, relief="solid", bd=1, fg="blue").grid(row=4, column=1, sticky="w", pady=6)

        tk.Checkbutton(user_content, text="Enable Auto-Trade", variable=self.auto_trade_active, 
                       bg=self.colors["panel"], fg=self.colors["brand"]).grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

        btnrow1 = tk.Frame(user_content, bg=self.colors["panel"])
        btnrow1.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 4))
        ttk.Button(btnrow1, text="Create User", command=self.create_user, style="Soft.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow1, text="Deposit Cash", command=self.deposit_cash, style="Soft.TButton").pack(side="left")

        btnrow2 = tk.Frame(user_content, bg=self.colors["panel"])
        btnrow2.grid(row=7, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Button(btnrow2, text="Buy", command=self.buy_share, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow2, text="Sell", command=self.sell_share, style="Soft.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow2, text="Market Snapshot", command=self.save_snapshot, style="Soft.TButton").pack(side="left")

        btnrow3 = tk.Frame(user_content, bg=self.colors["panel"])
        btnrow3.grid(row=8, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Button(btnrow3, text="Refresh Portfolio", command=self.refresh_portfolio, style="Soft.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btnrow3, text="Refresh Transactions", command=self.refresh_transactions, style="Soft.TButton").pack(side="left")

        summary_wrap, summary_content = self._section(top, "Portfolio Summary")
        summary_wrap.pack(side="left", fill="both", expand=True)
        self.summary_vars = {
            "cash": tk.StringVar(value="0.00"),
            "market": tk.StringVar(value="0.00"),
            "total": tk.StringVar(value="0.00"),
            "pnl": tk.StringVar(value="0.00"),
        }

        self._summary_card(summary_content, "Cash", self.summary_vars["cash"], 0, 0)
        self._summary_card(summary_content, "Holdings Value", self.summary_vars["market"], 0, 1)
        self._summary_card(summary_content, "Portfolio Value", self.summary_vars["total"], 1, 0)
        self._summary_card(summary_content, "PnL", self.summary_vars["pnl"], 1, 1)

        bottom = tk.Frame(self.tab_trade, bg=self.colors["bg"])
        bottom.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        left_bottom = tk.Frame(bottom, bg=self.colors["bg"])
        left_bottom.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right_bottom = tk.Frame(bottom, bg=self.colors["bg"])
        right_bottom.pack(side="left", fill="both", expand=True)

        hold_wrap, hold_content = self._section(left_bottom, "Portfolio Holdings")
        hold_wrap.pack(fill="both", expand=True)
        self.holdings_frame, self.holdings_tree = self._build_treeview(
            hold_content,
            columns=("Ticker", "Quantity", "Avg Buy", "Current", "Cost", "Market", "PnL"),
        )
        self.holdings_frame.pack(fill="both", expand=True)

        txn_wrap, txn_content = self._section(right_bottom, "Transactions")
        txn_wrap.pack(fill="both", expand=True)
        self.txn_frame, self.txn_tree = self._build_treeview(
            txn_content,
            columns=("Time", "Type", "Ticker", "Qty", "Price", "Total"),
        )
        self.txn_frame.pack(fill="both", expand=True)

    def _build_log_tab(self):
        wrap, content = self._section(self.tab_log, "Application Log")
        wrap.pack(fill="both", expand=True, padx=8, pady=8)
        tools = tk.Frame(content, bg=self.colors["panel"])
        tools.pack(fill="x", pady=(0, 8))
        ttk.Button(tools, text="Clear Log", command=self.clear_log, style="Soft.TButton").pack(side="left")
        self.log_text = tk.Text(content, wrap="word", bg="#1f2937", fg="#f9fafb", insertbackground="white", font=("Consolas", 10), relief="flat")
        self.log_text.pack(fill="both", expand=True)

    def log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.delete("1.0", "end")

    def _browse_single_output(self):
        path = filedialog.askdirectory()
        if path:
            self.single_output.set(path)

    def _browse_compare_output(self):
        path = filedialog.askdirectory()
        if path:
            self.compare_output.set(path)

    def refresh_user_combo(self):
        users = sorted(self.trading.users.keys())
        self.user_combo["values"] = users
        if users and not self.trade_user.get():
            self.trade_user.set(users[0])

    def _run_in_thread(self, target):
        threading.Thread(target=target, daemon=True).start()

    def run_single_analysis(self):
        def task():
            try:
                result = analyze_share(
                    self.single_ticker.get().strip(),
                    self.single_period.get().strip() or "1mo",
                    self.single_interval.get().strip() or "1d",
                    self.single_output.get().strip() or "stock_output",
                )
                self.current_analysis_result = result
                self.root.after(0, self.populate_single_analysis)
                self.root.after(0, lambda: messagebox.showinfo("Done", f"Analysis completed for {result['share']}"))
                self.log(f"Analysis completed for {result['share']}")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Error in single analysis: {e}")
        self._run_in_thread(task)

    def populate_single_analysis(self):
        result = self.current_analysis_result
        if not result:
            return
        for item in self.single_stats_tree.get_children():
            self.single_stats_tree.delete(item)

        stats = result["statistics"]
        for _, row in stats.iterrows():
            self.single_stats_tree.insert("", "end", values=(
                row.get("Column"),
                row.get("Count"),
                self._fmt(row.get("Mean")),
                self._fmt(row.get("Median")),
                self._fmt(row.get("Min")),
                self._fmt(row.get("Q1")),
                self._fmt(row.get("Q2")),
                self._fmt(row.get("Q3")),
                self._fmt(row.get("Max")),
                self._fmt(row.get("Std Dev (Population)")),
            ))

        chart_options = ["Close", "Volume", "Daily Return %", "Histogram"]
        self.single_chart_combo["values"] = [c for c in chart_options if self._single_chart_exists(c)]
        if self.single_chart_combo["values"]:
            self.single_chart_choice.set(self.single_chart_combo["values"][0])
            self.update_single_chart()

    def _single_chart_exists(self, name):
        df = self.current_analysis_result["data"]
        return ((name == "Close" and "Close" in df.columns) or
                (name == "Volume" and "Volume" in df.columns) or
                (name == "Daily Return %" and "Daily Return %" in df.columns) or
                (name == "Histogram" and "Close" in df.columns))

    def update_single_chart(self):
        if not self.current_analysis_result:
            return
        df = self.current_analysis_result["data"]
        choice = self.single_chart_choice.get()
        ax = self.single_ax
        ax.clear()

        if choice == "Close" and "Close" in df.columns:
            ax.plot(df.index, df["Close"], marker="o")
            ax.set_title(f"{self.current_analysis_result['share']} Close")
            ax.set_ylabel("Price")
        elif choice == "Volume" and "Volume" in df.columns:
            ax.bar(df.index, df["Volume"])
            ax.set_title(f"{self.current_analysis_result['share']} Volume")
            ax.set_ylabel("Volume")
        elif choice == "Daily Return %" and "Daily Return %" in df.columns:
            ax.plot(df.index, df["Daily Return %"], marker="o")
            ax.axhline(0)
            ax.set_title(f"{self.current_analysis_result['share']} Daily Return %")
            ax.set_ylabel("Return %")
        elif choice == "Histogram" and "Close" in df.columns:
            ax.hist(df["Close"].dropna(), bins=10)
            ax.set_title(f"{self.current_analysis_result['share']} Close Distribution")
            ax.set_xlabel("Close")
            ax.set_ylabel("Freq")

        ax.tick_params(axis="x", rotation=45)
        self.single_fig.tight_layout()
        self.single_canvas.draw()

    def run_comparison(self):
        def task():
            try:
                result = analyze_two_shares(
                    self.compare_ticker1.get().strip(),
                    self.compare_ticker2.get().strip(),
                    self.compare_period.get().strip() or "1mo",
                    self.compare_interval.get().strip() or "1d",
                    self.compare_output.get().strip() or "stock_compare_output",
                )
                self.current_comparison_result = result
                self.root.after(0, self.populate_comparison)
                self.root.after(0, lambda: messagebox.showinfo("Done", "Comparison completed"))
                self.log("Comparison completed.")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Error in comparison: {e}")
        self._run_in_thread(task)

    def populate_comparison(self):
        result = self.current_comparison_result
        if not result:
            return

        for item in self.compare_tree.get_children():
            self.compare_tree.delete(item)

        cdf = result["comparison_summary"]
        share1 = self.compare_ticker1.get().strip()
        share2 = self.compare_ticker2.get().strip()

        for _, row in cdf.iterrows():
            self.compare_tree.insert("", "end", values=(
                row.get("Column"),
                self._fmt(row.get(f"{share1} Mean")),
                self._fmt(row.get(f"{share2} Mean")),
                self._fmt(row.get(f"{share1} Std Dev")),
                self._fmt(row.get(f"{share2} Std Dev")),
                self._fmt(row.get(f"{share1} Min")),
                self._fmt(row.get(f"{share2} Min")),
                self._fmt(row.get(f"{share1} Max")),
                self._fmt(row.get(f"{share2} Max")),
            ))

        options = ["Close Comparison", "Normalized", "Daily Return %"]
        self.compare_chart_combo["values"] = options
        self.compare_chart_choice.set(options[0])
        self.update_compare_chart()

    def update_compare_chart(self):
        if not self.current_comparison_result:
            return

        share1 = self.compare_ticker1.get().strip()
        share2 = self.compare_ticker2.get().strip()
        df1 = self.current_comparison_result[share1]["data"]
        df2 = self.current_comparison_result[share2]["data"]
        common = df1.index.intersection(df2.index)
        df1 = df1.loc[common]
        df2 = df2.loc[common]

        ax = self.compare_ax
        ax.clear()
        choice = self.compare_chart_choice.get()

        if choice == "Close Comparison":
            ax.plot(df1.index, df1["Close"], marker="o", label=share1)
            ax.plot(df2.index, df2["Close"], marker="o", label=share2)
            ax.set_title("Close Price Comparison")
            ax.set_ylabel("Price")
            ax.legend()
        elif choice == "Normalized":
            n1 = df1["Close"] / df1["Close"].iloc[0] * 100
            n2 = df2["Close"] / df2["Close"].iloc[0] * 100
            ax.plot(df1.index, n1, marker="o", label=share1)
            ax.plot(df2.index, n2, marker="o", label=share2)
            ax.set_title("Normalized Performance (Base=100)")
            ax.set_ylabel("Base")
            ax.legend()
        elif choice == "Daily Return %":
            ax.plot(df1.index, df1["Daily Return %"], marker="o", label=share1)
            ax.plot(df2.index, df2["Daily Return %"], marker="o", label=share2)
            ax.axhline(0)
            ax.set_title("Daily Return % Comparison")
            ax.set_ylabel("Return %")
            ax.legend()

        ax.tick_params(axis="x", rotation=45)
        self.compare_fig.tight_layout()
        self.compare_canvas.draw()

    def create_user(self):
        try:
            self.trading.create_user(self.trade_user.get().strip(), float(self.trade_cash.get()))
            self.refresh_user_combo()
            self.log(f"Created user {self.trade_user.get().strip()}")
            messagebox.showinfo("Done", "User created.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Create user error: {e}")

    def deposit_cash(self):
        try:
            txn = self.trading.deposit_cash(self.trade_user.get().strip(), float(self.trade_cash.get()))
            self.log(f"Deposited {txn['amount']} for {txn['username']}")
            self.refresh_transactions()
            self.refresh_portfolio()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Deposit error: {e}")

    def buy_share(self):
        # --- ADDED: Auto-Trade Check ---
        if self.auto_trade_active.get():
            self._run_in_thread(lambda: self._run_algo_logic("BUY"))
            return

        def task():
            try:
                txn = self.trading.buy_share(self.trade_user.get().strip(), self.trade_ticker.get().strip(), int(self.trade_qty.get()))
                self.log(f"Bought {txn['quantity']} {txn['ticker']} at {txn['price']:.2f}")
                self.root.after(0, self.refresh_transactions)
                self.root.after(0, self.refresh_portfolio)
                self.root.after(0, lambda: messagebox.showinfo("Done", "Buy completed."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Buy error: {e}")
        self._run_in_thread(task)

    def sell_share(self):
        # --- ADDED: Auto-Trade Check ---
        if self.auto_trade_active.get():
            self._run_in_thread(lambda: self._run_algo_logic("SELL"))
            return

        def task():
            try:
                txn = self.trading.sell_share(self.trade_user.get().strip(), self.trade_ticker.get().strip(), int(self.trade_qty.get()))
                self.log(f"Sold {txn['quantity']} {txn['ticker']} at {txn['price']:.2f}")
                self.root.after(0, self.refresh_transactions)
                self.root.after(0, self.refresh_portfolio)
                self.root.after(0, lambda: messagebox.showinfo("Done", "Sell completed."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Sell error: {e}")
        self._run_in_thread(task)

    # --- ADDED: New Algo Logic Method ---
    def _run_algo_logic(self, mode):
        target = float(self.trade_target_price.get())
        ticker = self.trade_ticker.get().strip()
        user = self.trade_user.get().strip()
        qty = int(self.trade_qty.get())
        self.log(f"ALGO START: Waiting for {ticker} to hit {target} to {mode}")
        
        while self.auto_trade_active.get():
            try:
                price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
                if (mode == "BUY" and price <= target) or (mode == "SELL" and price >= target):
                    if mode == "BUY":
                        self.trading.buy_share(user, ticker, qty)
                    else:
                        self.trading.sell_share(user, ticker, qty)
                    
                    self.root.after(0, self.refresh_transactions)
                    self.root.after(0, self.refresh_portfolio)
                    self.root.after(0, lambda: messagebox.showinfo("Algo Success", f"Auto-{mode} executed at {price:.2f}"))
                    self.auto_trade_active.set(False)
                    break
                time.sleep(15) 
            except Exception as e:
                self.log(f"Algo Loop Error: {e}")
                break

    def refresh_portfolio(self):
        username = self.trade_user.get().strip()
        if not username:
            return
        def task():
            try:
                report = self.trading.get_portfolio_report(username)
                self.root.after(0, lambda: self.populate_portfolio(report))
                self.log(f"Refreshed portfolio for {username}")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Portfolio error: {e}")
        self._run_in_thread(task)

    def populate_portfolio(self, report):
        self.summary_vars["cash"].set(self._money(report["cash"]))
        self.summary_vars["market"].set(self._money(report["total_market_value"]))
        self.summary_vars["total"].set(self._money(report["total_portfolio_value"]))
        self.summary_vars["pnl"].set(self._money(report["total_pnl"]))

        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)

        for h in report["holdings"]:
            self.holdings_tree.insert("", "end", values=(
                h["ticker"], h["quantity"], self._fmt(h["avg_buy_price"]),
                self._fmt(h["current_price"]), self._money(h["cost_value"]),
                self._money(h["market_value"]), self._money(h["pnl"])
            ))

    def refresh_transactions(self):
        username = self.trade_user.get().strip()
        if not username:
            return
        try:
            txns = self.trading.get_user_transactions(username)
            for item in self.txn_tree.get_children():
                self.txn_tree.delete(item)
            for txn in reversed(txns[-200:]):
                self.txn_tree.insert("", "end", values=(
                    txn.get("timestamp", ""),
                    txn.get("type", ""),
                    txn.get("ticker", ""),
                    txn.get("quantity", ""),
                    self._fmt(txn.get("price", "")) if txn.get("price", "") != "" else "",
                    self._money(txn.get("total", 0)) if "total" in txn else self._money(txn.get("amount", 0)),
                ))
            self.log(f"Loaded {len(txns)} transaction(s) for {username}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"Transactions error: {e}")

    def save_snapshot(self):
        def task():
            try:
                ticker = self.trade_ticker.get().strip()
                self.trading.save_market_snapshot(ticker, "1mo", "1d")
                self.root.after(0, lambda: messagebox.showinfo("Done", f"Snapshot saved for {ticker}"))
                self.log(f"Market snapshot saved for {ticker}")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.log(f"Snapshot error: {e}")
        self._run_in_thread(task)

    def _money(self, x):
        try:    
            return f"{float(x):,.2f}"
        except Exception:
            return str(x)

    def _fmt(self, x):
        try:
            return f"{float(x):.4f}"
        except Exception:
            return str(x)


if __name__ == "__main__":
    root = tk.Tk()
    app = StockTradingGUI(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from model import ExpenseTracker


# --- Dialog Classes ---
# --- Add Expense Dialog ---

class AddExpenseDialog(tk.Toplevel):
    """
    Modal dialog for adding a new expense.
    Collects Amount, Category, and Date.
    """
    def __init__(self, master: tk.Tk, categories: List[str]):
        super().__init__(master)
        self.transient(master) # Keep the dialog on top of the main window
        self.title("Add New Expense")
        
        # Data storage and variables
        self.result: Optional[Tuple[float, str, str]] = None
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar(value=categories[0])
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        self._create_widgets(categories)
        
        # Make the dialog modal
        self.grab_set()
        master.wait_window(self) # Execution pauses here until dialog is destroyed

    def _create_widgets(self, categories: List[str]):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)

        # Input Fields
        ttk.Label(main_frame, text="Amount ($):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.amount_var).grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(main_frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.OptionMenu(main_frame, self.category_var, self.category_var.get(), *categories).grid(row=1, column=1, padx=5, sticky="ew")

        ttk.Label(main_frame, text="Date:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.date_var).grid(row=2, column=1, padx=5, sticky="ew")

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Submit", command=self._on_submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        
    def _on_submit(self):
        """Validates input, saves result, and closes the window."""
        try:
            amount = float(self.amount_var.get())
            date = self.date_var.get()
            
            if amount <= 0:
                messagebox.showerror("Input Error", "Amount must be positive.")
                return # Exit early
                
            # Store the validated data in the result attribute
            self.result = (amount, self.category_var.get(), date)
            
            # Close the dialog, which releases the wait_window call in the main class
            self.destroy() 
            
        except ValueError:
            messagebox.showerror("Input Error", "Invalid Amount or Date format.")
            return # Exit early


# --- Remove Expense Dialog ---

class RemoveExpenseDialog(tk.Toplevel):
    """
    Modal dialog for removing an expense.
    Collects the Expense ID.
    """
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.transient(master)
        self.title("Remove Expense")
        
        self.result: Optional[int] = None
        self.id_var = tk.StringVar()
        
        self._create_widgets()
        self.grab_set()
        master.wait_window(self)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Enter Expense ID:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.id_var, width=15).grid(row=0, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Remove", command=self._on_submit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

    def _on_submit(self):
        """Validates ID input, saves result, and closes the window."""
        try:
            expense_id = int(self.id_var.get())
            self.result = expense_id
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "ID must be a whole number.")
            return # Exit early


# --- Visualization Dialog ---

class ChartDialog(tk.Toplevel):
    """Modal dialog to display expense visualizations."""
    def __init__(self, master: tk.Tk, tracker: 'ExpenseTracker'):
        super().__init__(master)
        self.transient(master)
        self.title("Spending Visualization")

        self.geometry("600x500")
        
        self.tracker = tracker
        
        self._create_widgets()

        # Make the dialog modal
        self.grab_set()
        master.wait_window(self)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5) 

        ttk.Button(bottom_frame, text="Close Chart", command=self.destroy).pack(pady=5)


        # Get data from the model
        labels, values = self.tracker.get_spending_data_for_chart()
        
        if not values:
            ttk.Label(main_frame, text="No expense data available to chart.").pack(pady=20)
            return

        # Create a Matplotlib Figure
        fig = Figure(figsize=(7, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Draw the Pie Chart with placement controls
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'fontsize': 8},
            
            # --- FIX OVERLAP ---
            pctdistance=0.8, 
            labeldistance=1.1 # Pushes category labels slightly further out
        )
        ax.set_title("Spending Breakdown by Category")
        
        # Create the Tkinter Canvas Bridge
        canvas = FigureCanvasTkAgg(fig, master=main_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add the Navigation Toolbar
        toolbar = NavigationToolbar2Tk(canvas, main_frame)
        toolbar.update()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


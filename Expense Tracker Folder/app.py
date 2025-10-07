import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from model import ExpenseTracker
from dialogs import AddExpenseDialog, RemoveExpenseDialog, ChartDialog


# --- GUI Class ---

class ExpenseTrackerGUI:
    """Sets up the Tkinter GUI and interacts with the ExpenseTracker model."""
    def __init__(self, master: tk.Tk, tracker: ExpenseTracker):
        self.master = master
        self.tracker = tracker
        master.title("Personal Expense Tracker")
        
        self.categories = ["Food", "Rent", "Transport", "Clothes", "Home & Utilities", "Other"]

        self.filter_var = tk.StringVar(master, value="Filter by...")

        self._create_widgets()
        self._setup_expense_list()
        self._update_display()

        messagebox.showinfo("Info", "Click on column headers to sort.")

    def _create_widgets(self):
        """Sets up the main input and control widgets."""
        
        # Main button frame
        main_button_frame = ttk.LabelFrame(self.master, text="Expense Tracker Operations", padding="10")
        main_button_frame.pack(padx=10, pady=10, fill="x")

        # Add button
        ttk.Button(main_button_frame, text="Add Expense", command=self._open_add_dialog).grid(row=0, column=0, columnspan=2, pady=10)

        # Remove button
        ttk.Button(main_button_frame, text="Remove Expense", command=self._open_remove_dialog).grid(row=0, column=2, padx=10)

        # Export Button
        ttk.Button(main_button_frame, text="Export CSV", command=self._export_data_handler).grid(row=1, column=0, padx=10) # Using column 4 for placement

        # View Charts Button
        ttk.Button(main_button_frame, text="View Charts", command=self._open_chart_dialog).grid(row=1, column=2, padx=10)


        # Filter by.. dropdown
        filter_dropdown = ttk.Combobox(
            main_button_frame,
            values=["Filter by...", "All"] + self.categories,
            state="readonly",
            textvariable=self.filter_var,
            width=15,
        )
        filter_dropdown.grid(row=0, column=3, padx=10)

        # Bind the event to the handler method
        filter_dropdown.bind('<<ComboboxSelected>>', self._filter_handler)


        # --- Summary Label ---
        self.total_label = ttk.Label(self.master, text="Total Expenses: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=5)

        

    def _open_chart_dialog(self):
        """Opens the modal dialog with the spending chart."""
        # The dialog will automatically pull the data from self.tracker
        ChartDialog(self.master, self.tracker)

    def _setup_expense_list(self):
        """Sets up the Treeview widget and links it to a vertical Scrollbar."""

        # Create a Frame to hold the Treeview and Scrollbar together
        tree_frame = ttk.Frame(self.master, padding="10")
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("ID", "Date", "Category", "Amount")
        
        self.expense_list = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings',
            yscrollcommand=scrollbar.set # Links Treeview's scrolling to the scrollbar's position
        )
        self.expense_list.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar.config(command=self.expense_list.yview)

        # Column headings
        self.expense_list.heading("ID", text="ID")
        self.expense_list.column("ID", anchor=tk.CENTER, width=50)

        self.expense_list.heading("Date", text="Date")
        self.expense_list.column("Date", anchor=tk.CENTER, width=100)

        self.expense_list.heading("Category", text="Category")
        self.expense_list.column("Category", anchor=tk.CENTER, width=100)

        self.expense_list.heading("Amount", text="Amount")
        self.expense_list.column("Amount", anchor=tk.CENTER, width=80)

        # Enable sorting by clicking on column headers
        for col in columns:
            self.expense_list.heading(col, text=col, 
                command=lambda c=col: self._sort_treeview(c, False)) # Pass column name

        
            
    def _export_data_handler(self):
        """Prompts user for save location and triggers the CSV export."""
        
        # Open the 'Save As' file dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Expense Data"
        )

        if not filepath:
            # User canceled the dialog
            return

        # Call Model's export method
        success = self.tracker.export_expenses_to_csv(filepath)

        # Provide feedback
        if success:
            messagebox.showinfo("Export Success", f"Expense data saved to:\n{filepath}")
        else:
            messagebox.showerror("Export Failed", "Could not save data. Check console for details.")

    def _sort_treeview(self, col: str, reverse: bool):
        """Sorts the Treeview data when a column header is clicked."""

        # Get all data items and their values for the selected column
        data = [(self.expense_list.set(k, col), k) 
                for k in self.expense_list.get_children('')]

        # Sort the data list based on the column value
        if col == "Amount":
            data.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '')), reverse=reverse)
        elif col == "ID":
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        else:
            data.sort(key=lambda x: x[0], reverse=reverse)

        # Reinsert the sorted data into the Treeview
        for index, (val, k) in enumerate(data):
            self.expense_list.move(k, '', index)

        # Reverse the sort order for the next click
        self.expense_list.heading(col, 
            command=lambda c=col: self._sort_treeview(c, not reverse))

    def _filter_handler(self, event=None):
        """Handles filtering the expense list based on the selected category. Can be called without event to keep filter settings."""
        selected_category = self.filter_var.get()
        
        # Check for placeholder or "All" option
        if selected_category == "Filter by..." or selected_category == "All":
            # If showing all, use the Model's usual data
            data_to_display = self.tracker.get_all_expenses_data()
        else:
            # Get filtered list (Expense objects) from the model
            filtered_objects = self.tracker.get_filtered_expenses(selected_category)
            
            # Convert Expense objects to dicts for display
            data_to_display = [exp.to_dict() for exp in filtered_objects]

        # Update display with filtered data
        self._update_display(data_to_display)

    def _open_add_dialog(self):
        """Opens the dialog for adding an expense and completes the removal process"""
        dialog = AddExpenseDialog(self.master, self.categories)
        
        if dialog.result:
            # Unpack the returned tuple (amount, category, date)
            amount, category, date = dialog.result 
            
            try:
                # Add the expense to the Model
                self.tracker.add_expense(amount, category, date)
                self._filter_handler(None) # Refresh display with current filter
                messagebox.showinfo("Success", "Expense added.")
            except Exception as e:
                # Catch any unexpected errors
                messagebox.showerror("Error", f"Failed to add expense: {e}")

    def _open_remove_dialog(self):
        """Opens the modal dialog for removing an expense by ID and handles the result."""
        dialog = RemoveExpenseDialog(self.master)
        
        if dialog.result is not None:
            expense_id = dialog.result
            
            # Call the Model function
            success = self.tracker.remove_expense_by_id(expense_id)
            
            if success:
                self._filter_handler(None) # Refresh display with current filter
                messagebox.showinfo("Success", f"Expense ID {expense_id} removed.")
            else:
                messagebox.showerror("Error", f"Expense ID {expense_id} not found.")

    
    def _update_display(self, expense_data: Optional[List[Dict[str, Any]]] = None):
        """Refreshes the Treeview list and the summary label."""

        # If no specific data is passed (e.g., on initialization), get all data
        if expense_data is None:
            expense_data = self.tracker.get_all_expenses_data()

        # Clear existing list items
        for item in self.expense_list.get_children():
            self.expense_list.delete(item)
            
        # Calculate the total of the currently displayed expenses
        filtered_total = sum(float(expense['amount']) for expense in expense_data)

        # Get data from the Model and insert into Treeview
        for expense in expense_data: # Iterate over the provided list of dicts
            self.expense_list.insert('', tk.END, values=(
                expense['id'],
                expense['date'], 
                expense['category'], 
                f"${expense['amount']:.2f}"
            ))

        # Update Total Label
        self.total_label.config(text=f"Total Displayed Expenses: ${filtered_total:.2f}")


if __name__ == "__main__":
    # 1. Initialize the root GUI window
    root = tk.Tk()
    
    # 2. Initialize the Expense Tracker (Model)
    tracker = ExpenseTracker()

    # reset for testing
    # tracker._reset_expenses()

    # (Add initial dummy data for testing)
    # tracker.add_expense(50.00, "Food", "2025-10-01")
    # tracker.add_expense(1200.00, "Rent", "2025-10-03")
    # tracker.add_expense(15.75, "Transport", "2025-10-05")
    # tracker.add_expense(80.00, "Clothes", "2025-10-07")
    
    # 3. Initialize the GUI (View), passing the Model to it
    app = ExpenseTrackerGUI(root, tracker)
    
    # 4. Start the GUI loop
    root.mainloop()

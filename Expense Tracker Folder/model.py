from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
import csv



# --- Expense Class ---

class Expense:
    """Class for expense data."""

    static_id = 0  # Class variable to assign unique IDs

    def __init__(self, amount: float, category: str, date: str = None, id: int = None):
        """
        Initializes an Expense object.

        Args:
            amount (float): The monetary value of the expense.
            category (str): The category of the expense (e.g., Food, Rent).
            date (str, optional): The date of the expense. Defaults to today's date.
        """
        if date is None:
            self.date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.date = date
            
        if id is not None:
            self.id = id   
        else:  
            self.id = Expense.static_id
        Expense.static_id += 1

        self.amount = amount
        self.category = category
        

    def __str__(self) -> str:
        return f"{self.date} | {self.category}: ${self.amount:.2f}"

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation for easy saving."""
        return {"id": self.id, "date": self.date, "amount": self.amount, "category": self.category}


# --- Model ---

class ExpenseTracker:
    """Handles the list of expenses and file I/O."""
    def __init__(self, filename: str = "expenses.csv"):
        self.expenses: List[Expense] = []
        self.filename = filename
        self._load_data()

    def add_expense(self, amount: float, category: str, date: Optional[str] = None):
        """Creates an Expense object and adds it to the list."""
        try:
            expense = Expense(amount, category, date)
            self.expenses.append(expense)
            self._save_data()
        except ValueError:
            # Handle cases where amount is not convertible to float
            print("Error: Invalid amount provided.")

    def remove_expense_by_id(self, expense_id: int) -> bool:
        """Removes an expense from the list by ID. """
        old_count = len(self.expenses)
        
        # Use a list comprehension to filter out the expense with the matching ID
        self.expenses = [
            expense for expense in self.expenses 
            if expense.id != expense_id
        ]
        
        new_count = len(self.expenses)

        # Check if the list length changed
        if new_count < old_count:
            print(f"Removed expense with ID: {expense_id}")
            self._save_data() # Save the updated list to file
            return True
        else:
            print(f"Error: Expense with ID {expense_id} not found.")
            return False

    def get_spending_data_for_chart(self) -> Tuple[List[str], List[float]]:
        """
        Aggregates data by category and returns lists of labels and values
        ready for plotting.
        """
        summary = self.get_summary_by_category()
        
        # Filter out zero amounts and separate keys/values
        labels = []
        values = []
        for category, amount in summary.items():
            if amount > 0:
                labels.append(category)
                values.append(amount)
                
        return labels, values

    def get_summary_by_category(self) -> Dict[str, float]:
        """Calculates the total expense for each category."""
        summary: Dict[str, float] = {}
        for expense in self.expenses:
            summary[expense.category] = summary.get(expense.category, 0.0) + expense.amount
        return summary

    def get_all_expenses_data(self) -> List[Dict[str, Any]]:
        """Returns a list of dictionaries for display in the GUI."""
        return [exp.to_dict() for exp in self.expenses]
    
    def get_total_expense(self) -> float:
        """Returns the total of all recorded expenses."""
        return sum(exp.amount for exp in self.expenses)
    
    def _reset_expenses(self):
        """Clears all expenses (for testing purposes)."""
        self.expenses = []
        Expense.static_id = 0
        self._save_data()

    def get_filtered_expenses(self, category: Optional[str]) -> List[Expense]:
        """Returns a list of expenses by category."""
        if category and category != "All":
            return [
                exp for exp in self.expenses 
                if exp.category == category
            ]
        # If no filter is applied, return all expenses
        return self.expenses 

    def export_expenses_to_csv(self, filepath: str) -> bool:
        """
        Exports all current expense data to a specified CSV file path.
        """
        if not self.expenses:
            print("Export failed: No expenses to save.")
            return False

        # Get the data as a list of dictionaries
        data_to_export = [exp.to_dict() for exp in self.expenses]
        
        # Define the column headers for the CSV file
        fieldnames = ['id', 'date', 'category', 'amount'] 

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader() # Writes the column headers
                writer.writerows(data_to_export) # Writes the data rows
            
            return True
        except IOError:
            print(f"Error: Could not write to file {filepath}")
            return False

    # File I/O methods
    def _load_data(self):
        """Loads expenses from the JSON file and updates the static ID."""
    
        loaded_data = []
        try:
            with open(self.filename, 'r') as f:
                loaded_data = json.load(f)
        except FileNotFoundError:
            print(f"File {self.filename} not found. Starting with empty list.")
            return # Start empty if no file exists
        except json.JSONDecodeError:
            print(f"Error reading JSON from {self.filename}.")
            return

        max_id = -1
        for item in loaded_data:
            # Recreate the Expense object from the loaded dictionary item
            new_expense = Expense(
                amount=item['amount'],
                category=item['category'],
                date=item['date'],
                # Make sure expenses use their original ID, not a new one
                id=item['id'] 
            )
            self.expenses.append(new_expense)
            
            # Track the maximum ID found
            if item['id'] > max_id:
                max_id = item['id']

        # Set the static counter to the next available ID
        if max_id != -1:
            Expense.static_id = max_id + 1
            print(f"ID counter synchronized to {Expense.static_id}")
        
        print(f"Loaded {len(self.expenses)} expenses.")
        

    def _save_data(self):
        """Saves the current list of expenses to a json file."""
        data_to_save = [exp.to_dict() for exp in self.expenses]

        try:
            with open(self.filename, 'w') as f:
                # try to make readable with indent=4
                json.dump(data_to_save, f, indent=4)
            print(f"Saved {len(self.expenses)} expenses to {self.filename}")
        except IOError:
            print(f"Error: Could not write to file {self.filename}")

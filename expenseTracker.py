expenses = []

def addExpense(date, amount, category):
    expense = {'date': date, 'amount': amount, 'category': category}
    expenses.append(expense)

def listExpenses():
    if(len(expenses) == 0):
        print("You have no expenses recorded.\n\n")
        return
    
    print("\nHere is a list of your expenses:")
    counter = 0
        
    for expense in expenses:
        print("#", counter, " - ", expense['date'], " - ", expense['amount'], " - ", expense['category'])
        counter += 1
    print("\n\n")
        
def removeExpense():
    if(len(expenses) == 0):
        print("You have no expenses recorded.\n\n")
        return
    
    while True:
        listExpenses()
        print("What expense would you like to remove?")
        try:
            expenseToRemove = int(input("> "))
            del expenses[expenseToRemove]
            break
        except:     
            print("Invalid input. Please try again")
        

def printMenu():
    print("Choose an action below:")
    print("1 -> Add a new expense")
    print("2 -> Remove an expense")
    print("3 -> List all expenses")
    
    
    

if __name__ == "__main__":
    while True:
        # Prompt the user
        printMenu()
        optionSelected = input("> ")

        if(optionSelected == "1"):
            print("How much was this expense?")
            while True:
                try:
                    amountToAdd = input("> ")
                    break
                except:
                    print("Invalid input. Please try again")
            
            print("What category was this expense?")
            while True:
                try:
                    categoryToAdd = input("> ")
                    break
                except:
                    print("Invalid input. Please try again")
            addExpense(amountToAdd, categoryToAdd)
        elif(optionSelected == "2"):
            removeExpense()
        elif(optionSelected == "3"):
            listExpenses()
        else:
            print("Invalid option. Please try again.")
        
                
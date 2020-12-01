from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
import hashlib

from wtforms import StringField, SelectField, IntegerField, DateField

from Project3_Flask import main_functions

app = Flask(__name__)
app.config["SECRET_KEY"] = hashlib.sha256(b"include_a_strong_secret_key").hexdigest()  # mission accomplished?
app.config[
    "MONGO_URI"] = "mongodb+srv://some_dinkus:thisisatestpassword@cluster0.c4yii.mongodb.net/COP4813?retryWrites=true&w=majority"
app.config["MONGO_DBNAME"] = "COP4813"
mongo = PyMongo(app)
mongo_database = mongo.db
mongo_collection = mongo.db["expenses"]


class Expenses(FlaskForm):
    expense_category = main_functions.read_from_file("JSON_Files/expense_category.json")

    description = StringField("Description")
    category = SelectField("Category", choices=expense_category)
    cost = IntegerField("Cost")
    date = DateField("Date", format='%m/%d/%Y')


# Returns an expense total for a provided category
def get_total_expenses(category):
    expenses = mongo_collection.find({'category': int(category)})
    total = 0
    for expense in expenses:
        total += expense["cost"]
    return total


@app.route('/')
def index():
    my_expenses = mongo_collection.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    # print(total_cost)

    # Reads category data from a JSON file to allow for easy modification
    categories = main_functions.read_from_file("JSON_Files/expense_category.json")

    expensesByCategory = []
    for category in categories:
        category_id = category[0]
        name = category[1]
        expensesByCategory.append((name, get_total_expenses(category_id)))
    # print(expensesByCategory)

    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    expensesForm = Expenses(request.form)

    if request.method == "POST":
        description = request.form["description"]
        category = int(request.form["category"])
        cost = float(request.form["cost"])
        date = request.form["date"]

        expense = {'description': description, 'category': category, 'cost': cost, 'date': date}
        # ADD TO DB
        mongo_collection.insert_one(expense)

        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)


app.run()

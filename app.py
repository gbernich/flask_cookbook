from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask:python@localhost/flask_cookbook'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class Recipe(db.Model):
   id          = db.Column(db.Integer, primary_key = True)
   name        = db.Column(db.String(80), nullable=False)
   description = db.Column(db.String(500), nullable=True)
   servings    = db.Column(db.Integer, nullable=False)
   prep_time   = db.Column(db.Integer, nullable=False)
   cook_time   = db.Column(db.Integer, nullable=False)
   total_time  = db.Column(db.Integer, nullable=False)
   hot_cold    = db.Column(db.Enum("HOT", "COLD", name="hot_cold", create_type=False), nullable=False)
   meal_type   = db.Column(db.Enum("BREAKFAST", "LUNCH", "DINNER", "DESSERT", name="meal_type", create_type=False), nullable=False)
   
   calories      = db.Column(db.Integer, nullable=True)
   total_fat     = db.Column(db.Integer, nullable=True)
   saturated_fat = db.Column(db.Integer, nullable=True)
   cholesterol   = db.Column(db.Integer, nullable=True)
   sodium        = db.Column(db.Integer, nullable=True)
   carbohydrates = db.Column(db.Integer, nullable=True)
   fiber         = db.Column(db.Integer, nullable=True)
   sugar         = db.Column(db.Integer, nullable=True)
   protein       = db.Column(db.Integer, nullable=True)

   compliances   = db.relationship('RecipeCompliance',  backref="Recipe")
   ingredients   = db.relationship('RecipeIngredient',  backref="Recipe")
   instructions  = db.relationship('RecipeInstruction', backref="Recipe")
   logs          = db.relationship('RecipeLog',         backref="Recipe")
   #   clubs = db.relationship('studentclubs', backref="students")#, lazy='dynamic')

   def __init__(self, name, description, prep_time, cook_time, total_time, hot_cold, meal_type, calories, total_fat, saturated_fat, cholesterol, sodium, carbohydrates, fiber, sugar, protein):
      self.name          = name
      self.description   = description
      self.prep_time     = prep_time
      self.cook_time     = cook_time
      self.total_time    = total_time
      self.hot_cold      = hot_cold
      self.meal_type     = meal_type
      self.calories      = calories
      self.total_fat     = total_fat
      self.saturated_fat = saturated_fat
      self.cholesterol   = cholesterol
      self.sodium        = sodium
      self.carbohydrates = carbohydrates
      self.fiber         = fiber
      self.sugar         = sugar
      self.protein       = protein
#      self.clubs = []

class Compliance(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=True)
    
    def __init__(self, name):
        self.name = name
        
        
class Ingredient(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name):
        self.name = name
        
        
class Measure(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable=True)
    
    def __init__(self, name):
        self.name = name
        
        
class Preparation(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable=False)
    
    def __init__(self, name):
        self.name = name


class RecipeCompliance(db.Model):
    id            = db.Column(db.Integer, primary_key = True)
    recipe_id     = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    compliance_id = db.Column(db.Integer, db.ForeignKey(Compliance.id), nullable=False)

    compliance    = db.relationship('Compliance', backref="RecipeCompliance")
    
    def __init__(self, recipe_id, compliance_id):
        self.recipe_id     = recipe_id
        self.compliance_id = compliance_id


class RecipeIngredient(db.Model):
    id                 = db.Column(db.Integer, primary_key = True)
    recipe_id          = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    ingredient_id      = db.Column(db.Integer, db.ForeignKey(Ingredient.id), nullable=False)
    measure_id         = db.Column(db.Integer, db.ForeignKey(Measure.id), nullable=True)
    preparation_id     = db.Column(db.Integer, db.ForeignKey(Preparation.id), nullable=True)
    amount_whole       = db.Column(db.Integer, nullable=True)
    amount_numerator   = db.Column(db.Integer, nullable=True)
    amount_denominator = db.Column(db.Integer, nullable=True)
    
    ingredient         = db.relationship('Ingredient',  backref="RecipeIngredient")
    measure            = db.relationship('Measure',     backref="RecipeIngredient")
    preparation        = db.relationship('Preparation', backref="RecipeIngredient")

    def __init__(self, recipe_id, ingredient_id, measure_id, preparation_id, amount_whole, amount_numerator, amount_denominator):
        self.recipe_id          = recipe_id
        self.ingredient_id      = ingredient_id
        self.measure_id         = measure_id
        self.preparation_id     = preparation_id 
        self.amount_whole       = amount_whole
        self.amount_numerator   = amount_numerator
        self.amount_denominator = amount_denominator

    def __str__(self):
        return "Hello"

    def getAmountString(self):
        if (self.amount_numerator == 0 or self.amount_denominator == 0):
            return str(self.amount_whole)
        elif (self.amount_whole == 0):
            return str(self.amount_numerator) + "/" + str(self.amount_denominator)
        else:
            return str(self.amount_whole) + " " + str(self.amount_numerator) + "/" + str(self.amount_denominator)
        
    def getPreparationString(self):
        if (self.preparation == None or self.preparation.name == " "):
            return ""
        else:
            return " - " + self.preparation.name
            
    def getString(self):
        return self.getAmountString() + " " + self.measure.name + " " + self.ingredient.name + " " + self.getPreparationString()

class RecipeInstruction(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    recipe_id   = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    instruction = db.Column(db.String(320), nullable=True)

    def __init__(self, recipe_id, instruction):
        self.recipe_id   = recipe_id
        self.instruction = instruction


class RecipeLog(db.Model):
    id         = db.Column(db.Integer, primary_key = True)
    recipe_id  = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    cook_date  = db.Column(db.Date())
    notes      = db.Column(db.String(350), nullable=True)

    def __init__(self, recipe_id, cook_date, notes):
        self.recipe_id = recipe_id
        self.cook_date = cook_date
        self.notes     = notes
        
        
# class studentclubs(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    club = db.Column(db.String(100))
#    student_id = db.Column(db.Integer, db.ForeignKey(students.id), nullable=False)
#    student = db.relationship('students')

#    def __init__(self, club, student):
#       self.club = club
#       self.student = student

@app.route('/')
def show_all():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes = recipes )

@app.route('/display')
def display():
    id = request.args.get('id')
    recipe = Recipe.query.get(id)
    return render_template('displayLarge.html', recipe = recipe )
   
# @app.route('/new', methods = ['GET', 'POST'])
# def new():
#    if request.method == 'POST':
#       if not request.form['name'] or not request.form['city'] or not request.form['addr']:
#          flash('Please enter all the fields', 'error')
#       else:
#          student = students(request.form['name'], request.form['city'], request.form['addr'], request.form['pin'])

#          tmpClubs = []
#          for newclub in request.form['clubs'].split(', '):
#             club = studentclubs(newclub, student)
#             tmpClubs.append(club)
#          student.clubs.extend(tmpClubs)

#          db.session.add(student)
#          db.session.add_all(tmpClubs)
#          db.session.add(student)
#          db.session.commit()

#          flash('Record was successfully added')
#          return redirect(url_for('show_all'))
#    return render_template('new.html')

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True, host = '0.0.0.0')

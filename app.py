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

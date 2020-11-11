from flask import Flask, request, flash, url_for, redirect, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date
import re
import math
import json


# Constants
FILTERS_DEFAULT = {'hot_cold_hot':'', 'hot_cold_cold':'', \
                   'meal_type_breakfast':'', 'meal_type_lunch':'', \
                   'meal_type_dinner':'', 'meal_type_dessert':'', \
                   'ingredients':''}

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

    def __init__(self, name, description, servings, prep_time, cook_time, hot_cold, meal_type, calories, total_fat, saturated_fat, cholesterol, sodium, carbohydrates, fiber, sugar, protein):
        self.name          = name
        self.description   = description
        self.servings      = servings
        self.prep_time     = prep_time
        self.cook_time     = cook_time
        self.total_time    = str(int(self.prep_time) + int(self.cook_time))
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
    
    def __mul__(self, multiplier):
        # Create a dummy Recipe that won't be committed to the database
        dummy = Recipe(self.name, self.description, int(self.servings * multiplier), self.prep_time, self.cook_time, self.hot_cold, self.meal_type, self.calories, self.total_fat, self.saturated_fat, self.cholesterol, self.sodium, self.carbohydrates, self.fiber, self.sugar, self.protein)
        
        dummy.compliances = self.compliances
        dummy.instructions = self.instructions
        dummy.logs = self.logs
        
        # Loop through ingredients
        recipeIngredients = []
        for ingredient in self.ingredients:
            recipeIngredients.append(ingredient * multiplier)
        dummy.ingredients = recipeIngredients
        
        return dummy
        
    def getComplianceBlob(self):
        blob = ""
        for rc in self.compliances:
            blob += rc.compliance.name + '\n'
        return blob[:-1] # remove last newline
    
    def getIngredientBlob(self):
        blob = ""
        for ri in self.ingredients:
            blob += ri.getStringWithDelimiters() + '\n'
        return blob[:-1] # remove last newline
    
    def getInstructionBlob(self):
        blob = ""
        for ri in self.instructions:
            blob += ri.instruction + '\n'
        return blob[:-1] # remove last newline
        
    def filterRecipesByIngredients(recipes, ingredients):
        numIngredients  = len(ingredients)
        matchingRecipes = []
        
        for recipe in recipes:
            count = 0
            for ri in recipe.ingredients:
                recipeIngredient = ri.ingredient.name
                for filterIngredient in ingredients:
                    if (filterIngredient == recipeIngredient):
                        count += 1
                        if (count == numIngredients):
                            matchingRecipes.append(recipe)
                            break
                if (count == numIngredients):
                    break
            
        return matchingRecipes
                            
        
class Compliance(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=True)
    
    def __init__(self, name):
        self.name = name
        
    def getComplianceID(name):
        #print("getComplianceID: " + name)
        c = Compliance.query.filter_by(name=name).first()
        if c == None:
            # Add a new compliance and return ID
            new = Compliance(name)
            #print("new compliance:" + new.name)
            db.session.add(new)
            db.session.commit()
            c = Compliance.query.filter_by(name=name).first()
            #print("Newest: id: " + str(c.id), "name: " + c.name)
            return c.id
        else:
            #print("Found! id: " + str(c.id), "name: " + c.name)
            return c.id
        
    def getComplianceByName(name):
        #print("getComplianceID: " + name)
        c = Compliance.query.filter_by(name=name).first()
        if c == None:
            # Add a new compliance and return ID
            new = Compliance(name)
            #print("new compliance:" + new.name)
            db.session.add(new)
            db.session.commit()
            c = Compliance.query.filter_by(name=name).first()
            #print("Newest: id: " + str(c.id), "name: " + c.name)
            return c
        else:
            #print("Found! id: " + str(c.id), "name: " + c.name)
            return c
        
        
class Ingredient(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name):
        self.name = name
        
    def getIngredientByName(name):
        i = Ingredient.query.filter_by(name=name).first()
        if i == None:
            # Add a new compliance and return ID
            new = Ingredient(name)
            db.session.add(new)
            db.session.commit()
            return Ingredient.query.filter_by(name=name).first()
        else:
            # Return the Ingredient that was found
            return i
        
class Measure(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable=True)
    
    def __init__(self, name):
        self.name = name
        
    def getMeasureByName(name):
        m = Measure.query.filter_by(name=name).first()
        if m == None:
            # Add a new compliance and return ID
            new = Measure(name)
            db.session.add(new)
            db.session.commit()
            return Measure.query.filter_by(name=name).first()
        else:
            # Return the Measure that was found
            return m
        
        
class Preparation(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable=False)
    
    def __init__(self, name):
        self.name = name
        
    def getPreparationByName(name):
        p = Preparation.query.filter_by(name=name).first()
        if p == None:
            # Add a new compliance and return ID
            new = Preparation(name)
            db.session.add(new)
            db.session.commit()
            return Preparation.query.filter_by(name=name).first()
        else:
            # Return the Measure that was found
            return p


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

    def getRecipeIngredientFromText(text, recipeID):
        components  = text.split(',')
        amount      = components[0].strip()
        measure     = components[1].strip()
        ingredient  = components[2].strip()
        preparation = ' '
        if (len(components) > 3):
            preparation = components[3].strip()
            
        amountComponents = re.split('\s+|/', amount)
        if (len(amountComponents) == 3):
            amountWhole = int(amountComponents[0])
            amountNum   = int(amountComponents[1])
            amountDen   = int(amountComponents[2])
        elif (len(amountComponents) == 2):
            amountWhole = 0
            amountNum   = int(amountComponents[0])
            amountDen   = int(amountComponents[1])
        else:
            amountWhole = int(amountComponents[0])
            amountNum   = 0
            amountDen   = 0
            
        # handle measure
        measure = Measure.getMeasureByName(measure)
        
        # handle ingredient
        ingredient = Ingredient.getIngredientByName(ingredient)
        
        # handle preparation
        preparation = Preparation.getPreparationByName(preparation)
        
        return RecipeIngredient(recipeID, ingredient.id, measure.id, preparation.id, amountWhole, amountNum, amountDen)
            
    def getAmountString(self):
        if (int(self.amount_numerator) == 0 or int(self.amount_denominator) == 0):
            return str(self.amount_whole)
        elif (int(self.amount_whole) == 0):
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
        
    def getStringForShoppingList(self):
        return self.ingredient.name + " " + self.getPreparationString() + " (" + self.getAmountString() + " " + self.measure.name + ")"
        
    def getStringWithDelimiters(self):
        if (self.getPreparationString() == ""):
            return self.getAmountString() + ", " + self.measure.name + ", " + self.ingredient.name
        else:
            return self.getAmountString() + ", " + self.measure.name + ", " + self.ingredient.name + ", " + self.preparation.name
            
    def getDecimal(self):
        if (float(self.amount_denominator) > 0):
            return float(self.amount_whole) + float(self.amount_numerator) / float(self.amount_denominator)
        else:
            return float(self.amount_whole)
            
    def quantize(value):
        nums = [ 0, 1, 1, 2, 1, 3, 1, 3, 5, 7, 1 ] 
        dens = [ 1, 2, 3, 3, 4, 4, 8, 8, 8, 8, 1 ] 
        
        whole     = str(int(math.floor(value)))
        remainder = float(value) - float(math.floor(value))
        
        # calculate error for each fraction
        errors = []
        for i in range(0, len(nums)):
            errors.append(abs(remainder - (float(nums[i]) / float(dens[i]))))
        
        # return num/den for lowest error
        num = nums[errors.index(min(errors))]
        den = dens[errors.index(min(errors))]
        
        # set numerator and denominator to zero if they are both 1, this cleans up the displaying of the fraction
        if (num == 1 and den == 1):
            num = 0
            den = 0
        
        return whole, num, den
    
    def isCompatibleWith(self, other):
        if (self.ingredient_id == other.ingredient_id): 
            # ingredient matches
            if (self.measure_id == other.measure_id):
                # measurement matches
                return True
            # elif ():
            #     # matches a compatible measurement type
            else:
                # Attempt to just drop a trailing 's' to fix plural/singular issue
                selfSingular  = self.measure.name
                otherSingular = other.measure.name
                
                if (selfSingular[-1] == 's'):
                    selfSingular = selfSingular[:-1]
                if (otherSingular[-1] == 's'):
                    otherSingular = otherSingular[:-1]
                    
                if (selfSingular == otherSingular):
                    return True
        # if we reach here, return False
        return False
            
    def hasSameIngredientAs(self, other):
        if (self.ingredient_id == other.ingredient_id): 
            return True
        else:
            return False
        
    def __mul__(self, other):
        # RecipeIngredient * scalar
        whole, num, den = RecipeIngredient.quantize(float(other) * self.getDecimal())
        new = RecipeIngredient(self.recipe_id, self.ingredient_id, self.measure_id, self. preparation_id, whole, num, den)
        new.ingredient  = self.ingredient
        new.measure     = self.measure
        new.preparation = self.preparation
        return new
        
    def __add__(self, other):
        # RecipeIngredient + RecipeIngredient
        whole, num, den = RecipeIngredient.quantize(self.getDecimal() + other.getDecimal())
        new = RecipeIngredient(self.recipe_id, self.ingredient_id, self.measure_id, self. preparation_id, whole, num, den) 
        new.ingredient  = self.ingredient
        new.measure     = self.measure
        new.preparation = self.preparation
        return new
    
        
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

@app.route('/', methods = ['GET', 'POST'])
def show_all():
    if (request.method == 'GET'):
        # Show all recipes
        recipes = Recipe.query.all()
        
        filters = FILTERS_DEFAULT
        
        return render_template('index.html', recipes = recipes, filters = filters)
    
    else:
        # Filter based on form inputs
        filters = FILTERS_DEFAULT
        print(request.form)
        # Create query based on filters
        hot_cold = []
        if ('hot_cold_hot' in request.form):
            hot_cold.append("(Recipe.hot_cold == 'HOT')")
            filters['hot_cold_hot'] = 'checked'
        if ('hot_cold_cold' in request.form):
            hot_cold.append("(Recipe.hot_cold == 'COLD')")
            filters['hot_cold_cold'] = 'checked'
        
        meal_type = []
        if ('meal_type_breakfast' in request.form):
            meal_type.append("(Recipe.meal_type == 'BREAKFAST')")
            filters['meal_type_breakfast'] = 'checked'
        if ('meal_type_lunch' in request.form):
            meal_type.append("(Recipe.meal_type == 'LUNCH')")
            filters['meal_type_lunch'] = 'checked'
        if ('meal_type_dinner' in request.form):
            meal_type.append("(Recipe.meal_type == 'DINNER')")
            filters['meal_type_dinner'] = 'checked'
        if ('meal_type_dessert' in request.form):
            meal_type.append("(Recipe.meal_type == 'DESSERT')")
            filters['meal_type_dessert'] = 'checked'
        
        criteria = ''
        if (len(hot_cold) > 0):
            recipes = Recipe.query.filter(eval(' | '.join(hot_cold)))
            if (len(meal_type) > 0):
                recipes = recipes.filter(eval(' | '.join(meal_type)))
        
        elif (len(meal_type) > 0):
            recipes = Recipe.query.filter(eval(' | '.join(meal_type)))
            
        else:
            # no filters selected, show all
            recipes = Recipe.query.all()
            
        # filter by ingredient    
        if (len(request.form['ingredients'].strip()) > 0):
            ingredients = [x.strip().lower() for x in request.form['ingredients'].split(',')]
            if (len(ingredients) > 0):
                recipes = Recipe.filterRecipesByIngredients(recipes, ingredients)
                filters['ingredients'] = ', '.join(ingredients)
        return render_template('index.html', recipes = recipes, filters = filters)
        
        

@app.route('/display', methods = ['GET', 'POST'])
def display():
    id         = request.args.get('id')
    is_mobile  = request.args.get('is_mobile')
    multiplier = request.args.get('multiplier')
    recipe     = Recipe.query.get(id)
    
    if request.method == 'GET':
        return render_template('displayLarge.html', recipe = recipe, is_mobile = is_mobile, multiplier = multiplier )
    else:
        # POST
        
        # get multiplier
        if ('multiplier' in request.form):
            multiplier = request.form['multiplier']
        
        # Handle Multiplier POST
        if request.form['btn'] == 'Multiply':
            return render_template('displayLarge.html', recipe = recipe * float(multiplier), is_mobile = is_mobile, multiplier = multiplier )
            
        # Handle Shopping List POST
        elif request.form['btn'] == 'List':
            # append this recipe and multiplier to cookie
            cookie = request.cookies.get('shoppingListJSON')
            if cookie:
                shoppingList = json.loads(cookie)
                shoppingList['recipes'].append({'recipe_id': id, 'recipe_name': recipe.name, 'multiplier': multiplier})
            else:
                shoppingList = {'recipes':[{'recipe_id': id, 'recipe_name': recipe.name, 'multiplier': multiplier}]}
        
        # Handle Log POST
        elif request.form['btn'] == 'Log':
            # log notes for this recipe
            
            # Clean form data
            form = {}
            if (request.form['notes'] == '' or request.form['notes'] == None):
                notes = ""
            else:
                notes = request.form['notes'].strip()
            
            # Get recipe object from database
            id = request.args.get('id')
            recipe = Recipe.query.filter_by(id=id).first()
        
            # Create RecipeLog
            newRecipeLog = RecipeLog(id, date.today(), notes)
            db.session.add(newRecipeLog)
            
            # Update fields
            recipe.logs.append(newRecipeLog)
            db.session.commit()
            
            return render_template('displayLarge.html', recipe = recipe, is_mobile = is_mobile, multiplier = "1.0" )
            
        # recipes = Recipe.query.all()
        
        # filters = {'hot_cold_hot':'', 'hot_cold_cold':'', \
        #            'meal_type_breakfast':'', 'meal_type_lunch':'', \
        #            'meal_type_dinner':'', 'meal_type_dessert':'', \
        #            'ingredients':''}
        
        # resp = make_response(render_template('index.html', recipes = recipes, filters = filters))
        resp = make_response(redirect(url_for('list')))
        resp.set_cookie('shoppingListJSON', json.dumps(shoppingList))
        return resp

@app.route('/list', methods = ['GET', 'POST'])
def list():
    if request.method == 'GET' and request.cookies.get('shoppingListJSON'):
        shoppingRecipes = json.loads(request.cookies.get('shoppingListJSON'))
        
        # Combine ingredients lists
        ingredients = []
        for recipeItem in shoppingRecipes['recipes']:
            recipe = Recipe.query.get(recipeItem['recipe_id'])
            #print("\nRecipe: " + recipe.name + "   mult: " + recipeItem['multiplier'])
            
            # Loop through each ingredient
            for ri in recipe.ingredients:
                # Multiply ingredient
                tmp = ri * recipeItem['multiplier']
                
                # Check if its in the list already
                added = False
                if len(ingredients) == 0:
                    ingredients.append(tmp)
                    #print("first: " + ingredients[0].ingredient.name)
                else:
                    for idx in range(0, len(ingredients)):
                        #if (ri.ingredient_id == ingredients[idx].ingredient_id):
                        if (ri.isCompatibleWith(ingredients[idx])):
                            added = True
                            ingredients[idx] = ingredients[idx] + ri
                            #print("Adding to: " + ingredients[idx].ingredient.name)
                            break
                        elif (ri.hasSameIngredientAs(ingredients[idx])):
                            added = True
                            ingredients.insert(idx+1, ri)
                            #print("Inserting: " + ingredients[idx].ingredient.name)
                            break
                
                    # Add new ingredient to list
                    if (not added):
                        ingredients.append(tmp)
                        #print("new: " + ingredients[-1].ingredient.name)
        
        return render_template('list.html', shoppingRecipes = shoppingRecipes, ingredients = ingredients)
    else:
        # POST 
        resp = make_response(render_template('list.html', shoppingRecipes = None, ingredients = []))
        resp.delete_cookie('shoppingListJSON')
        return resp

@app.route('/add', methods = ['GET', 'POST'])
def add():
    if request.method == 'POST':
        
        # Clean form data
        form = {}
        for field in request.form:
            form[field] = request.form[field].strip()
            if(form[field] == ''):
                form[field] = None
        
        # Create recipe object
        recipe = Recipe(form['name'], form['description'], \
                        form['servings'], form['prep_time'], \
                        form['cook_time'], form['hot_cold'], \
                        form['meal_type'], form['calories'], \
                        form['total_fat'], form['saturated_fat'], \
                        form['cholesterol'], form['sodium'], \
                        form['carbohydrates'], form['fiber'], \
                        form['sugar'], form['protein'])

        # handle compliances
        recipeCompliances = []
        if (form['compliances'] != None):
            for c in form['compliances'].strip().lower().split('\n'):
                compliance = Compliance.getComplianceByName(c.strip())
                recipeCompliances.append(RecipeCompliance(recipe.id, compliance.id))
            recipe.compliances = recipeCompliances
            db.session.add_all(recipeCompliances)
        
        # handle ingredients
        recipeIngredients = []
        for i in form['ingredients'].strip().split('\n'):
            recipeIngredients.append(RecipeIngredient.getRecipeIngredientFromText(i, recipe.id))
            
        recipe.ingredients = recipeIngredients
        db.session.add_all(recipeIngredients)
        
        # handle instuctions
        recipeInstructions = []
        for i in form['instructions'].strip().split('\n'):
            recipeInstructions.append(RecipeInstruction(recipe.id, i.strip()))
        recipe.instructions = recipeInstructions
        db.session.add_all(recipeInstructions)
        
        # handle log
        recipe.logs = []
        
        # handle recipe
        db.session.add(recipe)
        db.session.commit()

        flash('Recipe was successfully added!')
        recipes = Recipe.query.all()
        filters = FILTERS_DEFAULT
        return render_template('index.html', recipes = recipes, filters = filters)
    # End if    
    return render_template('addRecipe.html')

@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    if request.method == 'POST':
        
        # Clean form data
        form = {}
        for field in request.form:
            form[field] = request.form[field].strip()
            if (form[field] == '' or form[field] == 'None'):
                form[field] = None
        
        # Get recipe object from database
        id = request.args.get('id')
        recipe = Recipe.query.filter_by(id=id).first()
        
        # Update fields
        recipe.name          = form['name']
        recipe.description   = form['description']
        recipe.servings      = form['servings']
        recipe.prep_time     = form['prep_time']
        recipe.cook_time     = form['cook_time']
        recipe.total_time    = str(int(recipe.prep_time) + int(recipe.cook_time))
        recipe.hot_cold      = form['hot_cold']
        recipe.meal_type     = form['meal_type']
        recipe.calories      = form['calories']
        recipe.total_fat     = form['total_fat']
        recipe.saturated_fat = form['saturated_fat']
        recipe.cholesterol   = form['cholesterol']
        recipe.sodium        = form['sodium']
        recipe.carbohydrates = form['carbohydrates']
        recipe.fiber         = form['fiber']
        recipe.sugar         = form['sugar']
        recipe.protein       = form['protein']

        # update recipe compliances by removing existing RecipeCompliances and re-adding 
        RecipeCompliance.query.filter_by(recipe_id=id).delete()
        recipeCompliances = []
        if (form['compliances'] != None):
            for c in form['compliances'].strip().lower().split('\n'):
                compliance = Compliance.getComplianceByName(c.strip())
                recipeCompliances.append(RecipeCompliance(recipe.id, compliance.id))
        recipe.compliances = recipeCompliances
        db.session.add_all(recipeCompliances)
        
        # update recipe ingredients by removing existing RecipeIngredients and re-adding
        RecipeIngredient.query.filter_by(recipe_id=id).delete()
        recipeIngredients = []
        for i in form['ingredients'].strip().split('\n'):
            recipeIngredients.append(RecipeIngredient.getRecipeIngredientFromText(i, recipe.id))
        recipe.ingredients = recipeIngredients
        db.session.add_all(recipeIngredients)
        
        # update recipe instuctions by removing existing RecipeInstructions and re-adding
        RecipeInstruction.query.filter_by(recipe_id=id).delete()
        recipeInstructions = []
        for i in form['instructions'].strip().split('\n'):
            recipeInstructions.append(RecipeInstruction(recipe.id, i.strip()))
        recipe.instructions = recipeInstructions
        db.session.add_all(recipeInstructions)
        
        # handle recipe
        #db.session.add(recipe)
        db.session.commit()

        flash('Recipe was successfully added!')
        recipes = Recipe.query.all()
        filters = FILTERS_DEFAULT
        return render_template('index.html', recipes = recipes, filters = filters)
    # End if
    # GET Method
    id         = request.args.get('id')
    recipe     = Recipe.query.get(id)
    return render_template('editRecipe.html', recipe = recipe)

if __name__ == '__main__':
   db.create_all()
   app.run(debug=True, host='0.0.0.0')

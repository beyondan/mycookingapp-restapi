from flask import Flask, jsonify, request
import mysql.connector
from util import gatherRecipeData

app = Flask(__name__)

dbconfig = {
    'user': "root",
    'password': "root",
    'database': "recipes",
    'host': "localhost"
}


@app.route('/search')
def search():
    query = request.args.get('q', default='', type=str)
    recipe_ids = []
    con = mysql.connector.connect(**dbconfig)
    cursor = con.cursor()

    # Gather all valid recipe_ids
    cursor.execute((
        "SELECT DISTINCT recipe_id "
        "FROM Recipes "
        "WHERE name LIKE %s"
    ), ("%" + query + "%",))
    for recipe_id in cursor:
        recipe_ids.append(recipe_id[0])

    cursor.execute((
        "SELECT DISTINCT ri.recipe_id "
        "FROM RecipeIngredients ri, Ingredients i "
        "WHERE ri.ingredient_id = i.ingredient_id "
        "AND i.name LIKE %s"
    ), ("%" + query + "%",))
    for recipe_id in cursor:
        recipe_ids.append(recipe_id[0])
    
    # Gather all relevant data for the filtered recipe_ids
    return jsonify(gatherRecipeData(recipe_ids, cursor))


@app.route('/recipes')
def recipes():
    con = mysql.connector.connect(**dbconfig)
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Recipes;")

    recipes = []
    for recipe_id, name, source, url in cursor:
        recipes.append({
            'recipe_id': recipe_id,
            'name': name,
            'source': source,
            'url': url
        })

    con.close()
    cursor.close()
    return jsonify(recipes)


@app.route('/')
def hello_world():
    return "hello, world!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)

import mysql.connector

dbconfig = {
    'user': "root",
    'password': "root",
    'database': "recipes",
    'host': "localhost"
}


def gatherRecipeData(recipe_ids, cursor):
    result = {} 

    if len(recipe_ids) == 0:
        return result

    recipe_ids = list(set(recipe_ids))

    # Get basic info
    cursor.execute((
        "SELECT recipe_id, name, source, url "
        "FROM Recipes "
        "WHERE " + format_in("recipe_id", recipe_ids)
    ))

    for recipe_id, name, source, url in cursor:
        result[recipe_id] = {
            'recipe_id': recipe_id,
            'name': name,
            'source': source,
            'source_url': url
        }

    # Get all image urls
    cursor.execute((
        "SELECT recipe_id, url "
        "FROM RecipeImages "
        "WHERE " + format_in("recipe_id", recipe_ids)
    ))

    for recipe_id, url in cursor:
        try:
            result[recipe_id]['image_urls'].append(url)
        except KeyError:
            result[recipe_id]['image_urls'] = [url]

    # Get all ingredients
    cursor.execute((
        "SELECT ri.recipe_id, i.name "
        "FROM RecipeIngredients ri, Ingredients i "
        "WHERE ri.ingredient_id = i.ingredient_id "
        "AND " + format_in("ri.recipe_id", recipe_ids)
    ))
    for recipe_id, ingredient_name in cursor:
        try:
            result[recipe_id]['ingredients'].append(ingredient_name)
        except KeyError:
            result[recipe_id]['ingredients'] = [ingredient_name]

    # Get all directions 
    cursor.execute((
        "SELECT recipe_id, step, direction "
        "FROM Directions "
        "WHERE " + format_in("recipe_id", recipe_ids)
    ))
    for recipe_id, step, direction in cursor:
        try:
            result[recipe_id]['directions'].append({
                'step': step,
                'direction': direction
            })
        except KeyError:
            result[recipe_id]['directions'] = [{
                'step': step,
                'direction': direction
            }]
    
    return list(result.values())


def format_in(column, include_list, exclude_list=None):
    include_list = list(map(str, include_list))
    include_list_s = ','.join(include_list)
    formatted = "{} IN ({})".format(column, include_list_s) 
    if exclude_list is not None:
        exclude_list = list(map(str, exclude_list))
        exclude_list_s = ','.join(exclude_list)
        formatted += " AND {} NOT IN ({})".format(column, exclude_list_s)
    return formatted

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.datastructures import ImmutableMultiDict

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)

with app.app_context():
    setup_db(app)
    CORS(app)
    db_drop_and_create_all()

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
    

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'], endpoint='get_drinks')
def drinks():
    """
    Public permission
    This API fetches all drinks with a short description
    Return the drinks array or the error handler
    """
    try:
        return json.dumps({
            'success': True,
            'drinks': [drink.short() for drink in Drink.query.all()]
        }), 200
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'], endpoint='drinks_detail')
@requires_auth('get:drinks-detail')
def drinks_detail(f):
    """
        Public permission
        This API fetches all drinks with a long description
        Return the drinks array or the error handler
        """
    try:
        return json.dumps({
            'success': True,
            'drinks': [drink.long() for drink in Drink.query.all()]
        }), 200
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'], endpoint='post_drink')
@requires_auth('post:drinks')
def drinks(f):
    """
     post:drinks permission
     This API creates a new drink and returns its long description
     Return the created drink info or the error handler
     """

    data = dict(request.form or request.json or request.data)
    drink = Drink(title=data.get('title'),
                  recipe=data.get('recipe') if type(data.get('recipe')) == str
                  else json.dumps(data.get('recipe')))
    try:
        drink.insert()
        return json.dumps({'success': True, 'drink': drink.long()}), 200
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'], endpoint='patch_drink')
@requires_auth('patch:drinks')
def drinks(f, id):
    """
     patch:drinks permission
     This API updates a drink if it exists
     Return the updated drink info or the error handler
     OBS: I would rather return a single object instead of an array, but POSTman test once again enforces it
     """
    try:
        data = dict(request.form or request.json or request.data)
        drink = drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.title = data.get('title') if data.get(
                'title') else drink.title
            recipe = data.get('recipe') if data.get('recipe') else drink.recipe
            drink.recipe = recipe if type(recipe) == str else json.dumps(
                recipe)
            drink.update()
            return json.dumps({'success': True, 'drinks': [drink.long()]}), 200
        else:
            return json.dumps({
                'success':
                False,
                'error':
                'Drink #' + id + ' not found to be edited'
            }), 404
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'], endpoint='delete_drink')
@requires_auth('delete:drinks')
def drinks(f, id):
    """
     delete:drinks permission
     This API deletes a drink if it exists
     Return the deleted drink info or the error handler
     """
    try:
        drink = drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink:
            drink.delete()
            return json.dumps({'success': True, 'drink': id}), 200
        else:
            return json.dumps({
                'success':
                False,
                'error':
                'Drink #' + id + ' not found to be deleted'
            }), 404
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 500

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Check the body request"
    }), 400

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Check the body request"
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
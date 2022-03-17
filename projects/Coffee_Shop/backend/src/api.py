import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()

        if not drinks:
            abort(404)

        drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except Exception as error:
        raise error




'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    try:
        drinks = Drink.query.all()

        if not drinks:
            abort(404)

        drinks = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

    except Exception as error:
        raise error

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        new_drink = request.get_json()

        title = json.loads(request.data)['title']
        if title == '':
            abort(400)

        drink = Drink(
            title=new_drink.get('title'),
            recipe=json.dumps(new_drink.get('recipe'))
        )
        
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 201

    except exc.SQLAlchemyError:
        abort(422)
    except Exception as error:
        raise error

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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        body = request.get_json()

        if not drink:
            abort(404)

        title = json.loads(request.data)['title']
        if title == '':
            abort(400)
        drink.title = title

        if 'recipe' in body:
            recipe = json.loads(request.data)['recipe']
            if not isinstance(recipe, list):
                abort(400)
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    # except exc.SQLAlchemyError:
    #     abort(422)
    except Exception as error:
        raise error

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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(
            Drink.id == drink_id
            ).one_or_none()

        if not drink:
            abort(404)
            
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200

    except exc.SQLAlchemyError:
        abort(422)
    except Exception as error:
        raise error

#-------------#
#Error Handlers
#-------------#

'''
Not Found
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": error.description
    }), 404

'''
Authentication
'''
@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.description
    }), error.status_code

@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': error.description
    }), 403

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': error.description
    }), 401

'''
Serverside
'''
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": error.description
    }), 500

'''
Request
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": error.description
    }), 405

if __name__ == "__main__":
    app.debug = True
    app.run()

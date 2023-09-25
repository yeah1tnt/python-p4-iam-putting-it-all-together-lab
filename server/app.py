#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        img = data.get('image_url')
        bio = data.get('bio')

        if username and password:
            user = User(username=username, image_url=img, bio=bio)
            user_dict = user.to_dict()
            user.password_hash = password

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user_dict, 201
        
        return {'error':'422 Unprocessable Entity'}, 422

            

class CheckSession(Resource):
    def get(self):
        # if 'user_id' in session:
        if session.get('user_id'):
            user = User.query.get(session['user_id'])
            return user.to_dict(), 200
        return {'error':'401 Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error':'401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error':'401 Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.get(session['user_id'])
            return [recipe.to_dict() for recipe in user.recipes], 200
        return {'error':'401 Unauthorized'}, 401
    
    def post(self):
        if session.get('user_id'):
            data = request.get_json()

            title = data['title']
            instructions = data['instructions']
            minutes_to_complete = data['minutes_to_complete']

            try:
                recipe = Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    # user_id=session['user_id']
                )


                recipe_dict = recipe.to_dict()
                recipe.user_id=session['user_id']

                db.session.add(recipe)
                db.session.commit()

                return recipe_dict, 201
            except IntegrityError:
                return {'error':'422 Unprocessable Entity'}, 422
        return {'error':'401 Unauthorized'}, 401

                

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

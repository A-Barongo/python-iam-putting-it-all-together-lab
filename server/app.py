#!/usr/bin/env python3

from flask import request, session,make_response,jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data['username'],
                image_url=data['image_url'],
                bio=data['bio']
            )
            user.password_hash = data['password'] 

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return make_response(jsonify(user.to_dict()), 201)

        except Exception as e:
            db.session.rollback()
            return {'error': 'There was an error while signing you up.'}, 422

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session['user_id']).first()
            
            return user.to_dict(), 200

        return {}, 401
        
class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username=data.get('username')
        user=User.query.filter(User.username==username).first()
        password=data.get('password')
        if user:
            if user.authenticate(password):
                session['user_id']=user.id
                return user.to_dict(),200
            
            else:
                return {'error':'Password or username is incorrect'},401
        else:
            return{'error':'Username not found'},401

class Logout(Resource):
    def delete(self):
        if not session['user_id']:
            return {'error': 'Not logged in'}, 401
        session['user_id']=None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            recipes=[recipe.to_dict() for recipe in Recipe.query.filter(Recipe.user_id==session['user_id']).all()]
            return make_response(jsonify(recipes),200)
        else:
            return {'error':'Unauthorized access'},401
        
    def post(self):

        request_json = request.get_json()

        title = request_json['title']
        instructions = request_json['_instructions']
        minutes_to_complete = request_json['minutes_to_complete']

        try:

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(), 201

        except IntegrityError:

            return {'error': '422 Unprocessable Entity'}, 422
        
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
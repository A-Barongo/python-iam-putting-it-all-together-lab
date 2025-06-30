from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-recipes.user', '-_password_hash',)
    
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False,unique=True)
    _password_hash =db.Column(db.String)
    image_url =db.Column(db.String)
    bio=db.Column(db.String)
    
    
    recipes=db.relationship('Recipe', backref='user')
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed")
    
    @password_hash.setter
    def password_hash(self,password):
        password_hash=bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash=password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    title=db.Column(db.String,nullable=False,unique=True)
    instructions=db.Column(db.String,nullable=False)
    minutes_to_complete=db.Column(db.Integer,nullable=False)
    
    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value or len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,  # ← missing
            'minutes_to_complete': self.minutes_to_complete,
            'user_id': self.user_id,
        }
    
    
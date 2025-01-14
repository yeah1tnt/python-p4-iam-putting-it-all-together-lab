from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    recipes = db.relationship('Recipe', backref='user')

    serialize_rules = ('-recipes.user','-_password_hash')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('password is not a readable attribute')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, db.CheckConstraint('len(instructions) <50'))
    minutes_to_complete = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('title')
    def validate_title(self, key, title):
        if title:
            return title
        raise ValueError('Title is required')
    
    # @validates('instructions')
    # def validate_instructions(self, key, instructions):
    #     if len(instructions) > 50:
    #         return instructions
    #     else:
    #         raise IntegrityError("IntegrityError", params={}, orig=None)

    # @validates('instructions')
    # def validate_instructions_length(self, key, instructions):
    #     if len(instructions) < 50:
    #         raise IntegrityError("IntegrityError", params={}, orig=None)
    #     else:
    #         return instructions
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
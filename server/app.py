from datetime import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_restful import Api

from models import db, Parent, Child, ChildParents

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

api = Api(app)

@app.route('/')
def index():
    return "<h1>Welcome to Child Adoption Api</h1>"

@app.route("/parents", methods=['GET'])
def get_parents():
    parents = Parent.query.all()
    return jsonify([parent.to_dict() for parent in parents]), 200


@app.route("/parents", methods=["POST"])
def create_parent():
    data = request.get_json()
    new_parent = Parent(
        name=data["name"],
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )
    db.session.add(new_parent)
    db.session.commit()
    return jsonify(new_parent.to_dict()), 201

@app.route("/parents/<int:id>", methods=["PATCH"])
def update_parent(id):
    parent = Parent.query.get(id)
    if not parent:
        return jsonify({"message": "Parent not found"}), 404
    
    try:
        data = request.get_json()
        
        for field in ["name", "username", "email", "password"]:
            if field in data:
                setattr(parent, field, data[field])
        
        db.session.commit()
        return jsonify(parent.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating parent", "error": str(e)}), 400
    
@app.route("/parents/<int:id>", methods=["DELETE"])
def delete_parent(id):
    parent = Parent.query.get(id)
    if not parent:
        return jsonify({"message": "Parent not found"}), 404
    
    try:
        ChildParents.query.filter_by(parent_id=id).delete()
        db.session.delete(parent)
        db.session.commit()
        
        return jsonify({"message": "Parent deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting parent", "error": str(e)}), 400

@app.route("/children", methods=['GET'])
def get_children():
    children = Child.query.all()
    return jsonify([child.to_dict() for child in children]), 200


@app.route("/children", methods=["POST"])
def create_child():
    data = request.get_json()
    new_child = Child(
        name=data["name"], 
        age=data["age"], 
        description=data["description"]
    )
    db.session.add(new_child)
    db.session.commit()
    return jsonify(new_child.to_dict()), 201

@app.route("/children/<int:id>", methods=["DELETE"])
def delete_childt(id):
    child = Child.query.get(id)
    if not child:
        return jsonify({"message": "Child not found"}), 404
    
    try:
        ChildParents.query.filter_by(child_id=id).delete()
        db.session.delete(child)
        db.session.commit()
        
        return jsonify({"message": "Child deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting child", "error": str(e)}), 400

@app.route("/adoptions", methods=["GET"])
def get_adoptions():
    adoptions = ChildParents.query.all()
    return jsonify([adoption.to_dict() for adoption in adoptions]), 200

@app.route("/children/<int:id>", methods=["PATCH"])
def update_child(id):
    child = Child.query.get(id)
    if not child:
        return jsonify({"message": "Child not found"}), 404
    
    try:
        data = request.get_json()
        
        for field in ["name", "age", "description"]:
            if field in data:
                setattr(child, field, data[field])
        
        db.session.commit()
        return jsonify(child.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating child", "error": str(e.__dict__)}), 400

@app.route("/adoptions", methods=["POST"])
def create_adoption():
    data = request.get_json()
    new_adoption = ChildParents(
        parent_id=data['parent_id'],
        child_id=data['child_id'],
        adoption_date=data['adoption_date'],
        status=data['status']
    )
    db.session.add(new_adoption)
    db.session.commit()
    return jsonify(new_adoption.to_dict()), 201

@app.route("/adoptions/<int:id>", methods=["DELETE"])
def delete_adoption(id):
    adoption = ChildParents.query.get(id)
    if adoption:
        db.session.delete(adoption)
        db.session.commit()
        return jsonify ({"message": "Adoption deleted"}), 200
    return jsonify({"message": "Adoption not found"}), 404

if __name__ == "__main__":
    app.run(port=5555, debug=True)
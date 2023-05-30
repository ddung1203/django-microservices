from dataclasses import dataclass
from flask import Flask, abort, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests

from producer import publish

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@main-mysql.default.svc.cluster.local/main'
CORS(app)

db = SQLAlchemy(app)

@dataclass
class Product(db.Model):
  id: int
  title: str
  image: str

  id = db.Column(db.Integer, primary_key=True, autoincrement=False)
  title = db.Column(db.String(200))
  image = db.Column(db.String(200))

@dataclass
class ProductUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  product_id = db.Column(db.Integer)
  
  __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='user_product_unique'),
    )


@app.route('/api/product')
def index():
  return jsonify(Product.query.all())

@app.route('/api/product/<int:id>/like', methods=['POST'])
def like(id):
  req = requests.get('http://admin-svc-np.default.svc.cluster.local:8000/api/user')
  json = req.json()

  try:
    productUser = ProductUser(user_id=json['id'], product_id=id)
    db.session.add(productUser)
    db.session.commit()

    publish('product_liked', id)

  except:
    abort(400, 'You already liked this product')


  return jsonify({
    'message': 'success'
  })

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')

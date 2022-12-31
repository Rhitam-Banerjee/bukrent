from flask import Blueprint, jsonify

from app.models.deliverer import Deliverer

api_delivery = Blueprint('api_delivery', __name__, url_prefix="/api_delivery")

@api_delivery.route('/get-deliverers')
def get_deliverers(): 
    deliverers = Deliverer.query.all()
    return jsonify({
        "status": "success",
        "deliverers": [deliverer.to_json() for deliverer in deliverers]
    })
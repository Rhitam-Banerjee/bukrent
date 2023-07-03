from flask import jsonify, make_response, request
from app.models.admin import Admin

from app.api_admin.utils import api_admin, token_required

import os
import jwt


@api_admin.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if not admin:
        return jsonify({
            "status": "error",
            "message": "Invalid username"
        }), 400
    if password != admin.password:
        return jsonify({
            "status": "error",
            "message": "Incorrect password"
        }), 400
    access_token_admin = jwt.encode({'id': admin.id}, os.environ.get('SECRET_KEY') or "SECRET", "HS256")
    response = make_response(jsonify({
        "status": "success",
        "admin": admin.to_json(),
    }), 200)
    response.set_cookie('access_token_admin', access_token_admin, secure=True, httponly=True, samesite='None')
    return response


@api_admin.route('/refresh')
@token_required
def refresh(admin):
    return jsonify({
        "status": "success",
        "admin": admin.to_json(),
    })


@api_admin.route('/logout', methods=['POST'])
@token_required
def logout(admin):
    response = make_response(jsonify({
        "status": "success",
    }))
    response.set_cookie('access_token_admin', '', secure=True, httponly=True, samesite='None')
    return response

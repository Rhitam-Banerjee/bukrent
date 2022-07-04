from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

api = Blueprint('api', __name__, url_prefix="/api")
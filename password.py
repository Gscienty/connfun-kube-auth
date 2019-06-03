import app
import session_stored
import mongo_client_builder
from flask import request, jsonify
import hashlib

'''
required:
    Header Content-Type: application/json
    Body {
        "username": "...",
        "password": "...",
        "hash_algo": "...(current only support md5)"
    }
'''
@app.app.route('/password/register', methods=[ 'POST' ])
def register_password_account():
    mongo_client = mongo_client_builder.build_mongo_client()

    if mongo_client.password_account.find_one({ 'account_name': request.json['username'] }):
        return jsonify({ msg: 'username existed' }), 400

    common_account_id = mongo_client.common_account.insert_one({
        'support': [ 'password' ],
        'role': [ ],
        'lock_expired': 0
        }).inserted_id

    hash_type = request.json['hash_algo'].lower()
    if hash_type == 'md5':
        hashed_password = hashlib.md5(request.json['password']).hexdigest().upper()
    else:
        return jsonify({ msg: 'not support {} hash algorithm'.format(hash_type) }), 400

    password_account_id = mongo_client.password_account.insert_one({
            'account_name': json['username'],
            'hash_algo': hash_type,
            'password': hashed_password,
            'refer_account_id': common_account_id
        }).inserted_id

    return jsonify({ msg: 'success' }), 201


@app.app.route('/password/new-password', methods=[ 'POST' ])
def set_password_account_new_password():
    pass


@app.app.route('/password/set-profile', methods=[ 'POST' ])
def set_password_profile():
    pass


@app.app.route('/password/sign-in')
def password_account_sign_in():
    pass


@app.app.route('/password/sign-out')
def password_account_sign_out():
    pass


@app.app.route('/password/lock')
def password_account_lock():
    pass


@app.app.route('/password/unlock')
def password_account_unlock():
    pass

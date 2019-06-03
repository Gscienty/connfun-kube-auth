import app
import session_stored
import mongo_client_builder
from flask import request, jsonify
import hashlib
import time

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
        return jsonify({ 'msg': 'username existed' }), 400

    common_account_id = mongo_client.common_account.insert_one({
        'support': [ 'password' ],
        'role': [ ],
        'lock_expired': 0
        }).inserted_id

    hash_type = request.json['hash_algo'].lower()
    if hash_type == 'md5':
        hashed_password = hashlib.md5(request.json['password']).hexdigest().upper()
    else:
        return jsonify({ 'msg': 'not support {} hash algorithm'.format(hash_type) }), 400

    password_account_id = mongo_client.password_account.insert_one({
            'account_name': request.json['username'],
            'hash_algo': hash_type,
            'password': hashed_password,
            'refer_account_id': common_account_id
        }).inserted_id

    return jsonify({ 'msg': 'success' }), 201

'''
    Header Content-Type: application/json
    Body {
        "username": "...",
        "hash_algo": "...",
        "password": "..."
    }
'''
@app.app.route('/password/new-password', methods=[ 'POST' ])
def set_password_account_new_password():
    mongo_client = mongo_client_builder.build_mongo_client()

    if not mongo_client.password_account.find_one({ 'account_name': request.json['username'] }):
        return jsonify({ 'msg': 'username existed' }), 400

    hash_type = request.json['hash_algo'].lower()
    if hash_type == 'md5':
        hashed_password = hashlib.md5(request.json['password']).hexdigest().upper()
    else:
        return jsonify({ 'msg': 'not support {} hash algorithm'.format(hash_type) }), 400

    mongo_client.password_account.update({
        'account_name': request.json['username']
        }, {
            '$set': {
                'password': hashed_password,
                'hash_algo': hash_type
                }
            })

    return jsonify({ 'msg': 'success' })

'''
    Header Content-Type: application/json
    Body {
        "id": "...",
        "profile": { ... }
    }
'''
@app.app.route('/password/set-profile', methods=[ 'POST' ])
def set_password_profile():
    mongo_client = mongo_client_builder.build_mongo_client()

    if mongo_client.user_profile.find_one({ 'refer_account_id': request.json['id'] }):
        mongo_client.user_profile.update({
            'refer_account_id': request.json['id']
            }, {
                '$set': request.json['profile']
                })
    else:
        profile = request.json['profile']
        profile['refer_account_id'] = request.json['id']
        mongo_client.user_profile.insert_one(profile)

    return jsonify({ 'msg': 'success' })


'''
    Header Content-Type: application/json
    Body {
        "username": "...",
        "password": "..."
    }
'''
@app.app.route('/password/sign-in')
def password_account_sign_in():
    mongo_client = mongo_client_builder.build_mongo_client()

    account = mongo_client.password_account.find_one({ 'account_name': request.json['username'] })
    if not account:
        return jsonify({ 'msg': 'account not existed' }), 404

    common_account = mongo_client.common_account.find_one({ '_id': account['refer_account_id'] })
    if time.time() <= common_account['lock_expired']:
        return jsonify({ 'msg': 'locked' }), 401

    if account['hash_algo'] == 'md5':
        hashed_password = hashlib.md5(request.json['password']).hexdigest().upper()
        if hashed_password != account['password']:
            return jsonify({ 'msg': 'password error' }), 400
    else:
        return jsonify({ 'msg': 'unsupport hash algo' }), 500

    # TODO temporary lock check

    # TODO session store

    # TODO return session key
    return jsonify({ 'msg': 'success', 'session_key': '' })


@app.app.route('/password/sign-out')
def password_account_sign_out():
    pass


@app.app.route('/password/lock')
def password_account_lock():
    pass


@app.app.route('/password/unlock')
def password_account_unlock():
    pass

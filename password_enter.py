import app
import session_stored
import mongo_client_builder
from flask import request, jsonify
import hashlib
import time
import os
import uuid
import account_temporary_locked
from bson.objectid import ObjectId

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
        'roles': [ ],
        'lock_expired': 0
        }).inserted_id

    mongo_client.user_profile.insert_one({
        'refer_account_id': common_account_id
        })

    hash_type = request.json['hash_algo'].lower()
    if hash_type == 'md5':
        hashed_password = hashlib.md5(request.json['password'].encode(encoding='UTF-8')).hexdigest().upper()
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
        hashed_password = hashlib.md5(request.json['password'].encode(encoding="UTF-8")).hexdigest().upper()
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
        "username": "...",
        "password": "..."
    }
'''
@app.app.route('/password/sign-in', methods=[ 'POST' ])
def password_account_sign_in():
    mongo_client = mongo_client_builder.build_mongo_client()

    account = mongo_client.password_account.find_one({ 'account_name': request.json['username'] })
    if not account:
        return jsonify({ 'msg': 'account not existed' }), 404

    common_account = mongo_client.common_account.find_one({ '_id': account['refer_account_id'] })
    if time.time() <= common_account['lock_expired']:
        return jsonify({ 'msg': 'locked' }), 401

    if account['hash_algo'] == 'md5':
        hashed_password = hashlib.md5(request.json['password'].encode(encoding='UTF-8')).hexdigest().upper()
        if hashed_password != account['password']:
            account_temporary_locked.account_temporary_attempt_times_inc(str(common_account['_id']), 24 * 60 * 60)
            return jsonify({ 'msg': 'password error' }), 400
    else:
        return jsonify({ 'msg': 'unsupport hash algo' }), 500

    attempt_times = account_temporary_locked.account_temporary_attempt_times(str(common_account['_id']))
    if attempt_times >= int(os.getenv('ATTEMPT_SIGN_IN_TIMES')):
        return jsonify({ 'msg': 'account locked' }), 403

    key = uuid.uuid5(uuid.NAMESPACE_OID, '{}-{}'.format(str(common_account['_id']), time.time()))
    session_stored.session_store(str(key), str(common_account['_id']))

    return jsonify({ 'msg': 'success', 'session_key': key })


'''
    Header Content-Type: application/json
    Body {
        "username": "...",
        "roles": [ "..." ]
    }
'''
@app.app.route('/password/role/add')
def password_account_role_add():
    db = mongo_client_builder.build_mongo_client()
    password_account = db.password_account.find_one({ 'account_name': request.json['username'] })
    if not password_account:
        return jsonify({ 'msg': 'account not exist' }), 404
    common_account = db.common_account.find_one({ "_id": password_account['refer_account_id'] })
    if not common_account:
        return jsonify({ 'msg': 'common account not exist' }), 404

    roles = set()
    for role in common_account['roles']:
        roles.add(role)
    for role in request.json['roles']:
        roles.add(role)
    roles_list = []
    for role in roles:
        roles_list.append(role)

    db.common_account.update({ '_id': common_account['_id'] }, { 'roles': roles_list })

    return jsonify({ 'msg': 'success' })


import app
import session_stored
import mongo_client_builder
from flask import request, jsonify
import os
from bson.objectid import ObjectId

'''
    Header Content-Type: application/json
    Body: {
        "session_key": "...",
        "roles": [ "..." ]
    }
'''
@app.app.route('/common/role/satisfy', methods=[ 'POST' ])
def common_role_satisfy():
    account_id = session_stored.session_get(request.json['session_key'])
    if not account_id:
        return jsonify({ 'msg': 'session not existed' }), 404
    
    db = mongo_client_builder.build_mongo_client()
    account = db.common_account.find_one({ '_id': ObjectId(account_id) })
    if not account:
        return jsonify({ 'msg': 'account not existed' }), 404

    account_roles = set()
    for role in account['roles']:
        account_roles.add(role)

    for role in request.json['roles']:
        if role not in account_roles:
            return jsonify({ 'msg': 'not satisfy' }), 400

    return jsonify({ 'msg': 'success' })


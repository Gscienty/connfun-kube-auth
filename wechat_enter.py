import app
import session_stored
import mongo_client_builder
from flask import request, jsonify
import os
import requests
from bson.objectid import ObjectId

'''
    Header Content-Type: application/json
    Body {
        "scope": "...",
        "state": "..."
    }
'''
@app.app.route('/wechat/oauth2/uri', methods=[ 'POST' ])
def wechat_oauth2_uri():
    auth_params = request.json
    req_uri = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    req_uri += '?appid={}'.format(os.getenv('SUB_APP_ID'))
    req_uri += '&redirect_uri={}'.format(wechat_sec.get_oauth_redirect_uri() if 'redirect_uri' not in auth_params else auth_params['redirect_uri'])
    req_uri += '&response_type=code'
    req_uri += '&scope={}'.format(auth_params['scope'])
    req_uri += '&state={}'.format(auth_params['state'] if 'state' in auth_params else '')
    req_uri += '#wechat_redirect'
    return jsonify({ 'uri': req_uri }), 200

'''
    Header Content-Type: application/json
    Body {
        "code": "...",
    }
'''
@app.app.route('/wechat/oauth2/access', methods=[ 'POST' ])
def wechat_oauth2_access():
    req_uri = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    req_uri += '?appid={}'.format(os.getenv('WECHAT_APP_ID'))
    req_uri += '&secret={}'.format(os.getenv('WECHAT_APP_SECRET'))
    req_uri += '&code={}'.format(request.json['code'])
    req_uri += '&grant_type=authorization_code'
    res = requests.get(req_uri)
    content = res.json()

    db = mongo_client_builder.build_mongo_client()
    wechat_account = db.wechat_account.find_one({ 'wechat_openid': content['openid'] })
    db = mongo_client_builder.build_mongo_client()
    if not wechat_account:
        common_account_id = db.common_account.insert_one({
            'support': [ 'wechat' ],
            'roles': [ ],
            'lock_expired': 0
            }).inserted_id
        db.wechat_account.insert_one({
            'wechat_openid': content['openid'],
            'wechat_token': content,
            'refer_account_id': common_account_id
            })
        db.user_profile.insert_one({
            'refer_account_id': common_account_id
            })
        wechat_account = db.wechat_account.find_one({ 'wechat_openid': content['openid'] })
    else:
        db.wechat_account.update({ 'wechat_openid': content['openid'] },
                { '$set': { 'wechat_token': content } })

    key = uuid.uuid5(uuid.NAMESPACE_OID, '{}-{}'.format(str(wechat_account['refer_account_id']), time.time()))
    session_stored.session_store(str(key), str(wechat_account['refer_account_id']))

    return jsonify({ 'msg': 'success', 'session_key': key, 'openid': content['openid'] }), 200


'''
    Header Content-Type: application/json
    Body {
        "session_key": "..."
    }
'''
@app.app.route('/wechat/oauth2/fresh', methods=[ 'POST' ])
def wechat_oauth2_fresh():
    common_account_id = session_stored.session_get('session_key')
    db = mongo_client_builder.build_mongo_client()
    wechat_account = db.wechat_account.find_one({ 'refer_account_id': ObjectId(common_account_id) })
    if not wechat_account:
        return jsonify({ 'msg': 'wechat account not existed' }), 404

    req_uri = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
    req_uri += '?appid={}'.format(os.getenv('WECHAT_APP_ID'))
    req_uri += '&grant_type=refresh_token'
    req_uri += '&refresh_token={}'.format(wechat_account['wechat_token']['token'])
    res = requests.get(req_uri)
    content = res.json()
    db.wechat_account.update({ 'refer_account_id': ObjectId(common_account_id) },
            { '$set': { 'wechat_token': content } })
    return jsonify({ 'msg': 'success' }), 200


'''
    Header Content-Type: application/json
    Body {
        "session_key": "..."
    }
'''
@app.app.route('/wechat/oauth2/userinfo', methods=[ 'POST' ])
def wechat_oauth2_userinfo():
    common_account_id = session_stored.session_get('session_key')
    db = mongo_client_builder.build_mongo_client()
    wechat_account = db.wechat_account.find_one({ 'refer_account_id': ObjectId(common_account_id) })
    if not wechat_account:
        return jsonify({ 'msg': 'wechat account not existed' }), 404

    req_uri = 'https://api.weixin.qq.com/sns/userinfo'
    req_uri += '?access_token={}'.format(wechat_account['wechat_token']['token'])
    req_uri += '&openid={}'.format(wechat_account['wechat_openid'])
    req_uri += '&lang=zh_CN'
    res = requests.get(req_uri)
    content = res.json()
    db.user_profile.update({ 'refer_account_id': ObjectId(common_account_id) },
            { '$set': { 'wechat_userinfo': content } })

    return jsonify(content), 200


'''
    Header Content-Type: application/json
    Body {
        "session_key": "...",
    }
'''
@app.app.route('/wechat/oauth2/verify', methods=[ 'POST' ])
def wechat_oauth2_verify():
    common_account_id = session_stored.session_get('session_key')
    db = mongo_client_builder.build_mongo_client()
    wechat_account = db.wechat_account.find_one({ 'refer_account_id': ObjectId(common_account_id) })
    if not wechat_account:
        return jsonify({ 'msg': 'wechat account not existed' }), 404

    req_uri = 'https://api.weixin.qq.com/sns/auth'
    req_uri += '?access_token={}'.format(wechat_account['wechat_token']['token'])
    req_uri += '&openid={}'.format(wechat_account['wechat_openid'])
    res = requests.get(req_uri)
    return jsonify(res.json()), 200


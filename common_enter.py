from flask import request, jsonify
import session_stored
import mongo_client_builder


'''
    Header Content-Type: application/json
    Body {
        "session_key": "...
    }
'''
@app.app.route('/common/sign-out')
def common_account_sign_out():
    session_key = request.json['session_key']
    session_stored.session_delete(session_key)
    return jsonify({ 'msg': 'success' })

'''
    Header Content-Type: application/json
    Body {
        "session_key": "..."
    }
'''
@app.app.route('/common/user-profile')
def common_user_profile():
    common_account_id = session_stored.session_get(request.json['session_key'])
    db = mongo_client_builder.build_mongo_client()
    profile = db.user_profile.find_one({ 'refer_account_id': ObjectId(common_account_id) })
    content = {}
    for key in profile:
        content[key] = profile[key]
    
    return jsonify(profile)


from flask import request, jsonify
import session_stored


'''
    Header Content-Type: application/json
    Body {
        "session_key": "...
    }
'''
@app.app.route('/common/sign-out')
def common_account_sign_out():
    key = request.json['session_key']
    session_stored.session_delete(key)
    return jsonify({ 'msg': 'success' })

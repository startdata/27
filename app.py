import datetime
import hashlib
import jwt
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

SECRET_KEY = "SPARTA"

# route


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def singup():
    return render_template('signup.html')

# add like


@app.route('/api/like', methods=['POST'])
def addLike():
    target = request.form['target']
    db.postings.find_one_and_update({"title": target}, {'$inc': {
        "like": 1
    }})
    return jsonify({'msg': '{target} 좋아요!'.format(target=target)})

# add dislike


@app.route('/api/dislike', methods=['POST'])
def addDislike():
    target = request.form['target']
    db.postings.find_one_and_update({"title": target}, {'$inc': {
        "dislike": 1
    }})
    return jsonify({'msg': '{target} 싫어요!'.format(target=target)})

# delete a post


@app.route('/api/delete', methods=['POST'])
def delete_star():
    target = request.form['target']
    db.mystar.find_one_and_delete({"name": target})
    return jsonify({'msg': '{target} 삭제되었습니다.}'.format(target=target)})

# register


@app.route('/api/signup', methods=['POST'])
def newSignup():
    id = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    user = {
        "id": id,
        "pw": pw_hash
    }
    db.users.insert_one(user)
    print(id, pw_hash)
    return jsonify({
        'result': 'success',
        "msg": '{id} 회원가입이 완료되었습니다!'.format(id=id)})


# login


@app.route('/api/login', methods=['POST'])
def api_login():
    id = request.form['id']
    pw = request.form['pw']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    print(pw_hash)
    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.users.find_one({'id': id, 'pw': pw_hash})

    print(result)
    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# logout


@app.route('/api/logout', methods=['POST'])
def api_logout():
    return jsonify({'result': "success", 'msg': '로그아웃되었습니다'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

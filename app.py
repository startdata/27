import datetime
import hashlib
from flask.helpers import url_for
import requests
import jwt
from pymongo import MongoClient
from bs4 import BeautifulSoup
from bson.objectid import ObjectId

from flask import Flask, render_template, jsonify, request
from requests.api import post
from werkzeug.utils import redirect

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

SECRET_KEY = "SPARTA"

# Web Crawling
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

# route


@app.route('/')
def home():
    postings = list(db.postings.find({}))
    for posting in postings:
        posting["_id"] = str(posting["_id"])

    # 로그인, 로그아웃 텍스트 바꾸기 위해 토큰 확인
    try:
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('main.html', postings=postings, isLoggedIn=True)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('main.html', postings=postings, isLoggedIn=False)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/join')
def singup():
    return render_template('join.html')


@app.route('/detail/<postingId>')
def detail(postingId):
    print(postingId)
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posting = db.postings.find_one({"_id": ObjectId(postingId)})
        # 좋아요 수 변경
        # print(posting)
        return render_template('detail.html', posting=posting)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

# add like


@app.route('/api/like', methods=['POST'])
def addLike():
    postingId = request.form['postingId']
    try:
        foundPosting = db.postings.find_one_and_update({"_id": ObjectId(postingId)}, {'$inc': {
            "like": 1
        }})
        return jsonify({'msg': '{target} 좋아요!'.format(target=foundPosting["title"])})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


# add dislike


@app.route('/api/dislike', methods=['POST'])
def addDislike():
    postingId = request.form['postingId']
    print(postingId)
    try:
        foundPosting = db.postings.find_one_and_update({"_id": ObjectId(postingId)}, {'$inc': {
            "dislike": 1
        }})
        print(foundPosting["dislike"])
        return jsonify({'msg': '{target} 싫어요!'.format(target=foundPosting["title"])})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


# register


@app.route('/api/join', methods=['POST'])
def newSignup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    if db.users.find({"id": id_receive}).count() > 0:
        return jsonify({
            "result": "failure",
            "msg": "이미 존재하는 계정입니다."
        })

    hashedPw = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    user = {
        "id": id_receive,
        "hashedPw": hashedPw,
        "postings": [],
    }
    db.users.insert_one(user)

    return jsonify({
        'result': 'success',
        "msg": '{id} 회원가입이 완료되었습니다!'.format(id=id)})


# login


@app.route('/api/login', methods=['POST'])
def apiLogin():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    hashedPw = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    user = db.users.find_one({'id': id_receive, 'hashedPw': hashedPw})
    if user is not None:
        payload = {
            'id': user["id"],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# logout


@app.route('/api/logout', methods=['POST'])
def apiLogout():
    return jsonify({'result': "success", 'msg': '로그아웃되었습니다'}) if request.cookies.get("mytoken") == None else jsonify({"result": "failure", "msg": "로그아웃에 실패하였습니다."})


@app.route('/api/url', methods=['POST'])
def apiPosting():
    # 현재 접속중인 사람이 누군지 알기 위해서 토큰 복호화
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = db.users.find_one({"id": payload['id']})
    # 스크래핑
    url = request.form['url']
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    title = soup.select_one(
        '#content > div.article > div.mv_info_area > div.mv_info > h3 > a:nth-child(1)').text

    # 중복 확인
    # if db.postings.find({"title": title}) != None:
    #     return redirect(url_for("home"))

    description = soup.select_one(
        '#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div.story_area > p').text

    # 요소에서 장르의 텍스트만 추출해서 배열에 저장
    genresArray = []
    genres = soup.select(
        '#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p > span:nth-child(1) > a')
    for genre in genres:
        genresArray.append(genre.text)

    imageUrl = soup.select_one(
        '#content > div.article > div.mv_info_area > div.poster > a > img')['src']
    # db.postings collection에 저장하기
    posting = {
        "url": url,
        "title": title,
        "description": description,
        "like": 0,
        "dislike": 0,
        "owner": user["id"],
        "comments": [],
        "genres": genresArray,
        "imageUrl": imageUrl
    }

    db.postings.insert_one(posting)

    # user에도 저장하기
    db.users.update_one(
        user, {"$push": {'postings': posting}})

    return jsonify({'result': "success", 'msg': '포스팅 완료!'})

# delete a post


@app.route('/api/delete', methods=['POST'])
def apiDelete():
    title = request.form['title']
    # 현재 접속중인 사람이 누군지 알기 위해서 토큰 복호화
    token = request.cookies.get('mytoken')
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = db.users.find_one({"id": payload['id']})
    # 쿼리에 dictionary 타입을 쓸 수 없는데, 그래서 ObjectId 타입을 string으로 변환
    # 그리고 그걸 다시 ObjectId 타입으로 변환해서 쿼리에 사용
    # postId = str(post['_id'])
    # db.postings.delete_one(post)
    db.postings.find_one_and_delete(
        {"title": title, "owner": user["id"]})

    db.users.find_one_and_update({"id": user["id"]}, {"$pull": {
        "postings": {"title": title}
    }})

    return jsonify({"result": "success", 'msg': '{target} 삭제되었습니다.'.format(target=title)})

# Add comment


@app.route('/api/add-comment', methods=['POST'])
def addComment():
    # 타겟이 될 포스팅
    id = request.form['id']
    message = request.form['message']

    # 댓글 작성자를 알기 위해 토큰 가져오기
    try:
        token = request.cookies.get('mytoken')
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        userId = db.users.find_one({"id": payload['id']})["id"]

        comment = {
            "author": userId,
            "message": message
        }

        db.postings.find_one_and_update({"_id": ObjectId(id)}, {
            '$push': {
                "comments": comment}
        })
        return jsonify({'result': "success", 'msg': '댓글 추가 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

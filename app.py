from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

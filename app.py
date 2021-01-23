from os import stat
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, request, session
app = Flask(__name__)
app.secret_key = "4scf54f85s"
client = MongoClient(port=27017)
db = client.flask_todo


@app.route('/', methods=['POST', 'GET'])
def index():
    session['authentic'] = False
    return render_template("index.html", data={"loginFailed": False, "regPass": False})


@app.route('/login', methods=['POST', 'GET'])
def Authorize():
    if request.method == 'POST':
        formData = request.form
        try:
            y = db.users.count_documents(
                {"userId": formData['id'], "password": formData['psw']})
        except:
            return render_template("index.html", data={"loginFailed": True, "regPass": False})
        if y == 1:
            userInfo = db.users.find_one({"userId": formData['id']})
            session['userName'] = userInfo['userName']
            session['userId'] = userInfo['userId']
            session['authentic'] = True
            todos = db.todos.find({"userId": session['userId']})
            return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos})

        else:
            return render_template("index.html", data={"loginFailed": True, "regPass": False})
    else:
        return render_template("index.html", data={"loginFailed": False, "regPass": False})


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template("registration.html", data={"regFailed": False})
    else:
        formData = request.form
        try:
            db.users.insert_one({"userName": formData['fname'], "userId": formData['email'],
                                 "password": formData['psw'], "mobile": formData['mobile']})
            return render_template("index.html", data={"loginFailed": False, "regPass": True})
        except:
            return render_template("registration.html", {"regFailed": True})


@app.route('/addTodo', methods=["POST", "GET"])
def addTodo():
    if session['authentic']:
        if request.method == "GET":
            return render_template("newTodo.html", data={"userName": session['userName'], "userId": session['userId'], "added": False})
        else:
            formData = request.form
            db.todos.insert_one(
                {"userId": session['userId'], "description": formData["desc"], "date": formData['date'], "time": formData['time'], "status": "Upcoming"})
            return render_template("newTodo.html", data={"userName": session['userName'], "userId": session['userId'], "added": True})
    else:
        return render_template("index.html", data={"loginFailed": False, "regPass": False})


@app.route('/home', methods=["GET"])
def goHome():
    if session['authentic']:
        if request.method == "GET":
            todos = db.todos.find({"userId": session['userId']})
            return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos})
    else:
        return render_template("index.html", data={"loginFailed": False, "regPass": False})


@app.route('/update', methods=["GET"])
def updateTodo():
    id = request.args.get('todoid')
    desc = request.args.get('desc')
    date = request.args.get('date')
    time = request.args.get('time')
    status = request.args.get('status')
    try:
        print(id)
        print(desc)
        print(date)
        print(time)
        print(status)
        updated = {"$set": {"description": desc,
                            "date": date, "time": time, "status": status}}
        up = db.todos.update_one({"_id": ObjectId(id)}, updated)

    except Exception as e:
        print(e)
        todos = db.todos.find({"userId": session['userId']})
        return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos, "deleteFailed": True})
    todos = db.todos.find({"userId": session['userId']})
    return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos})


@app.route('/delete', methods=["GET"])
def deleteTodo():
    id = request.args.get('todoid')
    try:
        res = db.todos.delete_one({"_id": ObjectId(id)})

    except:
        todos = db.todos.find({"userId": session['userId']})
        return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos, "deleteFailed": True})
    todos = db.todos.find({"userId": session['userId']})
    return render_template("home.html", data={"userId": session['userId'], "userName": session['userName'], "authentic": session['authentic'], "todos": todos})


if __name__ == "__main__":
    app.run(debug=True)

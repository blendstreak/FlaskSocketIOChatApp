from flask import Flask, render_template, redirect, request, session, url_for
from flask_socketio import SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "smallSecret!"
socketio = SocketIO(app)

users = {}
members = 0

def generate_unique_code(codeLen):
	while True:
		code = ""
		for _ in range(0, codeLen):
			code += random.choice(ascii_uppercase)
		if code not in users:
			break
	return code

@app.route("/", methods=["POST", "GET"])
def home():
	global members
	session.clear()
	if request.method == "POST":
		name = request.form.get("name")
		join = request.form.get("join", False)
		
		if not name:
			return render_template("home.html", error="Enter a name!")
			
		if join != False:
			code = generate_unique_code(6)
			session["code"] = code
			session["name"] = name
			users[code] = name
			users["chat"] = {"messages": []}
			members += 1
			return redirect(url_for("chat"))
			
	return render_template("home.html")

@app.route("/chat")
def chat():
	name = session.get("name")
	code = session.get("code")
	
	if name is None or code is None or code not in users:
		return redirect(url_for("home"))
	return render_template("chat.html", name=name, messages=users["chat"]["messages"])
	
@socketio.on("message")
def handle_message(message):
	uid = session.get("code")
	name = session.get("name")
	if uid not in users:
		return
	content = {"name": name, "message": message["data"]}
	socketio.send(content)
	users["chat"]["messages"].append(content)

@socketio.on("connect")
def response():
    name = session.get("name")
    content = {"name": name + "  (", "message": "Entered the chat!"}
    socketio.send(content)

@socketio.on("disconnect")
def removeUser():
	global members
	uid = session.get("code")
	name = session.get("name")
	content = {"name": name + "  )", "message": "Left the chat..."}
	socketio.send(content)
	if members > 0:
		members -= 1
		del users[uid]

# if __name__ == "__main__":
# 	socketio.run(app, debug=False, host='0.0.0.0')

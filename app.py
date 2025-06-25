from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import json, os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATA_FILE = "events.json"

# Load events from file
def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Save events to file
def save_events(events):
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=4)

# Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        session["user"] = user
        session["color"] = "#4da6ff" if user == "John" else "#ff69b4"
        return redirect("/calendar")
    return render_template("login.html")

# Calendar Page
@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        date = request.form.get("date", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        user = session["user"]

        if not date or not title:
            return 'Missing data', 400

        events = load_events()
        found = False
        for e in events:
            if e["date"] == date and e.get("user") == user:
                e["title"] = title
                e["description"] = description
                found = True
                break
        if not found:
            events.append({
                "date": date,
                "title": title,
                "description": description,
                "user": user
            })
        save_events(events)
        return '', 204

    return render_template("index.html", user=session["user"])

# Serve events
@app.route("/events")
def get_events():
    events = load_events()
    current_user = session.get("user")
    user_color = session.get("color", "#4da6ff")

    formatted = [
        {
            "title": e["title"],
            "start": e["date"],
            "description": e.get("description", ""),
            "color": user_color if e.get("user") == current_user else "#ff69b4"
        }
        for e in events
    ]
    return jsonify(formatted)

# Delete event
@app.route("/delete", methods=["POST"])
def delete_event():
    date = request.form.get("date", "").strip()
    title = request.form.get("title", "").strip()
    user = session.get("user")

    if not date or not title or not user:
        return 'Invalid delete request', 400

    events = load_events()
    updated = [
        e for e in events
        if not (e["date"] == date and e.get("user") == user and e["title"] == title)
    ]
    save_events(updated)
    return '', 204

# Account Page
@app.route("/account")
def account():
    if "user" not in session:
        return redirect("/")
    user = session["user"]
    events = [e for e in load_events() if e.get("user") == user]
    return render_template("account.html", events=sorted(events, key=lambda x: x["date"]), user=user)

# Color Preference
@app.route("/update_color", methods=["POST"])
def update_color():
    if "user" not in session:
        return redirect("/")
    color = request.form.get("color")
    if color:
        session["color"] = color
    return redirect("/account")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

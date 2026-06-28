from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import mysql.connector
from groq import Groq
import json
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "ideaforge_secret_2024"

from config import DB_CONFIG
client = Groq(api_key="gsk_xxxxxxxxxx")
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name FROM professions ORDER BY name")
    professions = [row["name"] for row in cursor.fetchall()]
    cursor.close(); db.close()
    return render_template("form.html", professions=professions)

@app.route("/generate", methods=["POST"])
def generate():
    profession  = request.form.get("profession", "")
    custom_prof = request.form.get("custom_profession", "").strip()
    experience  = request.form.get("experience", "Intermediate")
    tech_stack  = request.form.get("tech_stack", "")
    count       = int(request.form.get("count", 3))

    final_profession = custom_prof if custom_prof else profession

    prompt = f"""You are a creative tech mentor. Generate {count} unique project ideas for:
- Profession: {final_profession}
- Experience Level: {experience}
- Preferred Tech Stack: {tech_stack if tech_stack else 'any relevant technologies'}

Respond ONLY with a valid JSON array, no extra text, no markdown:
[
  {{
    "title": "Project Title",
    "description": "2-3 sentence description",
    "tech": "Recommended tech stack",
    "difficulty": "Beginner OR Intermediate OR Advanced",
    "features": ["Feature 1", "Feature 2", "Feature 3"],
    "github_tip": "One tip for making this stand out on GitHub"
  }}
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    ideas = json.loads(raw)

    db = get_db()
    cursor = db.cursor()
    for idea in ideas:
        cursor.execute("""
            INSERT INTO generated_ideas
            (profession, experience_level, tech_stack, idea_title, idea_description, difficulty, features)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            final_profession, experience, idea.get("tech"),
            idea.get("title"), idea.get("description"),
            idea.get("difficulty"), json.dumps(idea.get("features", []))
        ))
    db.commit()
    cursor.close(); db.close()

    session["ideas"] = ideas
    session["profession"] = final_profession
    session["experience"] = experience
    return redirect(url_for("results"))

@app.route("/results")
def results():
    ideas = session.get("ideas", [])
    profession = session.get("profession", "")
    experience = session.get("experience", "")
    if not ideas:
        return redirect(url_for("form"))
    return render_template("results.html",
        ideas=ideas,
        profession=profession,
        experience=experience
    )

if __name__ == "__main__":
    app.run(debug=True)
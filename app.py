import json
import sqlite3

from flask import Flask, jsonify, redirect, render_template

from gen_openai import gen_scene, gen_scenes

app = Flask(__name__)


SAMPLE_SCENE = {
    "title": "Stillness of the Forest",
    "image": "https://cdn.leonardo.ai/users/9130cf8e-bad3-409f-bc7a-f26ee62f1ff7/generations/acef7c09-aa27-49a9-bb09-b32695f026b0/lost_forest_2_Lurking_Shadows_forest_scene_0.jpg",
    "on_discover": {
        "description": "The dense forest holds a profound stillness, its tranquility and beauty washing away your worries. You are overcome with a feeling of calm and peace.",
        "stats": [{"stat": "vigor", "diff": 2}, {"stat": "courage", "diff": 2}],
    },
    "on_return": {
        "description": "The peace and calm of the forest still linger, giving you a renewed sense of confidence.",
        "stats": [{"stat": "vigor", "diff": 1}, {"stat": "courage", "diff": 1}],
    },
}

DATABASE = "lost.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY,
            info TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def save_scene(scene):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO scenes (info) VALUES (?)", (json.dumps(scene),))
    conn.commit()
    conn.close()


init_db()


@app.route("/seed", methods=["GET"])
def seed():
    save_scene(SAMPLE_SCENE)
    return redirect("/scenes")


@app.route("/gen", methods=["GET"])
def gen():
    scene = gen_scene()
    save_scene(scene)
    return redirect("/scenes")


@app.route("/gen/<n>", methods=["GET"])
def gen_n(n):
    for scene in gen_scenes(int(n)):
        save_scene(scene)
    return redirect("/scenes")


@app.route("/scene", methods=["GET"])
def pop_scene():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM scenes ORDER BY id DESC LIMIT 1")
    scene = c.fetchone()
    if scene:
        scene_id, scene_info = scene
        c.execute("DELETE FROM scenes WHERE id = ?", (scene_id,))
        conn.commit()
        conn.close()
        return jsonify(json.loads(scene_info))
    else:
        conn.close()
        return jsonify({"message": "No scenes available"})


@app.route("/scenes", methods=["GET"])
def list_scenes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT info FROM scenes ORDER BY id DESC")
    scenes = [json.loads(row[0]) for row in c.fetchall()]
    conn.close()
    return render_template("scenes.html", scenes=scenes)


if __name__ == "__main__":
    app.run(debug=True)

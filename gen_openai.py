import concurrent.futures
import json
import os
import sqlite3
import time
from textwrap import dedent

import openai

from gen_leonardo import gen_image

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")


def gen_scenes(n):
    print(f"Generating {n} scenes...")
    scenes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_result = {executor.submit(gen_scene): i for i in range(n)}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_result)):
            print(f"Scene {i} done")
            scene = future.result()
            if scene is not None:
                scenes.append(scene)
    return scenes


def gen_scene():
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt='I\'m making scenes for a game.  The setting is being lost in the forest.  Each scene has a unique feature that can be frightening, inspiring, relaxing, etc.  The scene can feature an encounter that is either animal, natural, human, or supernatural.\nThe player has two stats: vigor and courage.  Vigor is impacted by events that give or take energy and effort.  Courage is impacted by events that add or reduce fear and uncertainty.\nA scene has title and 1-2 sentence initial description of what you see and how it effects you (in second person).  \nIt also has stat change of one, both, or neither of the player stats.  Changes should be an integer between -4 and 4.\nA scene also has returning description that highlights any potential changes and how they impact you and a corresponding returning stat change.\n\nOutput format is a single JSON map:\n\n{\n  "title": "Intimidating Bear",\n  "on_discover": {\n    "description": "A massive bear stands tall, its powerful presence filling you with both awe and fear. You tread cautiously, knowing any sudden movement could provoke its fierce wrath. Best not to linger.",\n    "stats": [\n      {\n        "stat": "courage",\n        "diff": -2\n      }\n    ]\n  },\n  "on_return": {\n    "description": "The bear is still here, or has it been following you?",\n    "stats": [\n      {\n        "stat": "courage",\n        "diff": -4\n      }\n    ]\n  }\n}\n\n\n\n',
        temperature=1.10,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    try:
        scene_json = response["choices"][0]["text"]
        # sometimes the LLM generated json escaping doesn't work
        scene_json = scene_json.replace("\\'", "'")
        scene = json.loads(scene_json)
    except Exception as e:
        print("Error getting scene info", e, scene_json)
        return

    try:
        image_url = gen_image(scene["title"], scene["on_discover"]["description"])
        scene["image"] = image_url
    except Exception as e:
        print("Error generating scene image", e)

    return scene


def fine_tune():
    DATABASE = "lost.db"
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT info FROM scenes ORDER BY id DESC")
    data = [json.loads(row[0]) for row in c.fetchall()]
    conn.close()
    instructions = dedent(
        """
        Help the user make up scenes for a game. The setting is being lost in a forest. Scenes have different feelings and involve various encounters.
        The output must follow a specific JSON map.  The only valid stats are `vigor` and `courage`.
        """
    ).strip()

    def to_msg(sample):
        sample.pop("image")
        return {
            "messages": [
                {
                    "role": "system",
                    "content": instructions,
                },
                {"role": "user", "content": ""},
                {
                    "role": "assistant",
                    "content": json.dumps(sample),
                },
            ]
        }

    with open("output.jsonl", "w") as f:
        for scene in data:
            f.write(json.dumps(to_msg(scene)) + "\n")

    with open("output.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f]

    # Initial dataset stats
    print("Num examples:", len(dataset))
    print("First example:")
    for message in dataset[0]["messages"]:
        print(message)

    input("DO YOU WANT TO CONTINUE?")

    upload = openai.File.create(file=open("output.jsonl", "rb"), purpose="fine-tune")
    n = 0
    while True or n > 5:
        n += 1
        time.sleep(1)
        f = openai.File.retrieve(upload.id)
        if f["status"] == "processed":
            break
    res = openai.FineTuningJob.create(training_file=f["id"], model="gpt-3.5-turbo")
    print(res)


if __name__ == "__main__":
    input("ABOUT TO RUN FINE TUNING!  ARE YOU SURE?")
    fine_tune()

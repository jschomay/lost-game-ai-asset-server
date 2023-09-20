import os
import time

import requests

BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
WAIT_TIME = 10

token = os.getenv("LEONARDO_TOKEN")


def gen_image(title, desc):
    """
    Best image gen params:

    - use "lost forest sparse" model
    - Guidance scale of 10
    - prompt magic turned on (V2 high contrast on, strength 0.4)
    - prompt should be "forest scene - <title>: <full description>"
        eg: forest scene - Mystic Grove: Within a hollow, your every sound
        reverberates, creating an eerie symphony of echoes. The effect is both
        haunting and captivating, drawing you into the forest's auditory secrets.


    """
    payload = {
        "height": 512,
        # lost forest sparse model
        "modelId": "1c9986ee-ffd5-485b-b9a6-2289dd10a8d6",
        "prompt": f"forest scene - {title}: {desc}",
        "width": 512,
        "guidance_scale": 11,
        "num_images": 1,
        "promptMagic": True,
        "promptMagicVersion": "v2",
        "public": False,
        "highContrast": True,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    response = requests.post(BASE_URL + "/generations", json=payload, headers=headers)
    response.raise_for_status()
    gen_id = response.json()["sdGenerationJob"]["generationId"]
    time.sleep(WAIT_TIME)
    return get_gen(gen_id)


def get_gen(gen_id):
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
    }

    attempts = 0
    while attempts < 10:
        response = requests.get(BASE_URL + "/generations/" + gen_id, headers=headers)
        response.raise_for_status()
        status = response.json()["generations_by_pk"]["status"]
        if status == "FAILED":
            raise Exception(f"Generation {gen_id} failed")
        if status == "COMPLETE":
            return response.json()["generations_by_pk"]["generated_images"][0]["url"]

        print(f"generation {gen_id} not ready, waiting {WAIT_TIME} seconds..")
        attempts += 1
        time.sleep(WAIT_TIME)

    raise Exception(f"Generation {gen_id} failed after {attempts} attempts")

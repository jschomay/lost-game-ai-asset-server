
Prompt:

    I'm making scenes for a game.  The setting is being lost in the forest.  Each scene has a unique feature that can be frightening, inspiring, relaxing, etc.  The scene can feature an encounter that is either animal, natural, human, or supernatural.
    The player has two stats: vigor and courage.  Vigor is impacted by events that give or take energy and effort.  Courage is impacted by events that add or reduce fear and uncertainty.
    A scene has title and 1-2 sentence initial description of what you see and how it effects you (in second person).  
    It also has stat change of one, both, or neither of the player stats.  Changes should be an integer between -4 and 4.
    A scene also has returning description that highlights any potential changes and how they impact you and a corresponding returning stat change.

    Output format is a single JSON map:

    {
      "title": "Intimidating Bear",
      "on_discover": {
        "description": "A massive bear stands tall, its powerful presence filling you with both awe and fear. You tread cautiously, knowing any sudden movement could provoke its fierce wrath. Best not to linger.",
        "stats": [
          {
            "stat": "courage",
            "diff": -2
          }
        ]
      },
      "on_return": {
        "description": "The bear is still here, or has it been following you?",
        "stats": [
          {
            "stat": "courage",
            "diff": -4
          }
        ]
      }
    }


## Todo

Where I'm at:
- I can generate a scene from nothing yay!!
- I decided to use sqlite as a simple embedded file system db and it is working fine
- I am triggering sample gen scenes by api and saving them
- I have a simple gallery of scenes in the db
- I'm using legacy completion endpoint for training because it is more reliable I have found
- validate scenes when they come back before generating image
- save scene as a callback after each scene gen

What I need next:
- add api key for gen endpoints
- Disable extra unused routes
- upload to fly.io
- make change to game
- Check Leonardo CDN retention policy



## Planning approach

Strategy for gathering training data:

Small python script (using code above) to get completions in a loop 50(?) times.
Each completion gets written to its own json file in training_data/

Manually validate/edit all results.

Then a second python script that reads all files in that directory and uses each one
for training (might need to seriialize the json first?)

Note, the legacy completion model seems more consistent that chat.
Also the above prompt seems to work well 100% of the time, so training may not be
necessary... but I'll try it on both modes to see how it goes.


Strategy for live generation:

Node (or python?) server that exposes an endpoint to get a new scene.
Scenes are cached, so it just "pops the stack" (somehow in postgres?)
It caches more if the cached amount gets too low.

To cache:
In a loop, call the OpenAI completions end point like above but with the trained model.
Parse out description to call Leonardo api and get the cdn url back.
(check cdn retention policy)
Add filename to the json, serialize it and cache it.

Cache preview server:
Might be nice to see what we've got.  A simple page that grabs and renders 50 scenes
from the cache with a formatted output of the image and metadata as a grid of cards.

* Could preview the preview server using the training data first.


Questions:

- Do I make this as its own service with sqlite on fly.io, or build it directly into
  replit with their db?  replit has secrets for openai etc but having a service is
  nice
- How do I lock on refresh check? (and do the check after returning the result?)
- Load 16 even if they are not used or grab 1 on scene enter and manage them




Example outputs:



Title: Fluttering in the Breeze
Initial description: You look up and see colorful butterflies in the clearing. The sun gives them a celestial glow and brings you a sense of hope and peace.
Initial impact: Vigor +3, Courage +2
Returning description: After joyfully chasing dozens of these magical creatures, you feel a new surge of energy and increased courage.
Returning impact: Vigor +4, Courage +3


{
    "title": "Majestic Waterfall",
    "on_discover": {
        "description":
        "A magnificent waterfall cascades down into a pond of clear, cool blue water below. The peaceful sound of the water's rush fills you with an inspiring tranquility.",
        "stats": [{
            "stat": "confidence",
            "diff": 2
        }]
    },
    "on_return": {
        "description":
        "The waterfall has not changed, its beauty restored by the gently flowing water.",
        "stats": [{
            "stat": "confidence",
            "diff": 4
        }]
    }
}


{
  "title": "Stillness of the Forest",
  "on_discover": {
    "description": "The dense forest holds a profound stillness, its tranquility and beauty washing away your worries. You are overcome with a feeling of calm and peace.",
    "stats": [
      {
        "stat": "vigor",
        "diff": 2
      },
      {
        "stat": "courage",
        "diff": 2
      }
    ]
  },
  "on_return": {
    "description": "The peace and calm of the forest still linger, giving you a renewed sense of confidence.",
    "stats": [
      {
        "stat": "vigor",
        "diff": 1
      },
      {
        "stat": "courage",
        "diff": 1
      }
    ]
  }
}



{
  "title": "Stumbling in the Dark",
  "on_discover": {
    "description": "As the last light of day fades away, you’re left alone in the dark, navigating an unfamiliar forest. You find yourself unbalanced and uneasy as you stumble along.",
    "stats": [
      {
        "stat": "vigor",
        "diff": -2
      },
      {
        "stat": "courage",
        "diff": -1
      }
    ]
  },
  "on_return": {
    "description": "The darkness persists and you can’t help but feel as if something lurks beyond your vision. You become more frantic as you struggle to find your way.",
    "stats": [
      {
        "stat": "vigor",
        "diff": -4
      },
      {
        "stat": "courage",
        "diff": -2
      }
    ]
  }
}


{
  "title": "Terrifying Howl",
  "on_discover": {
    "description": "A horrifying howl shatters the still of the night sending a chill up your spine. It's coming from all directions, yet you can't seem to place what manner of being is making this sound.",
    "stats": [
      {
        "stat": "courage",
        "diff": -4
      }
    ]
  },
  "on_return": {
    "description": "The howl still echoes throughout the forest. Dare you go towards the source?",
    "stats": [
      {
        "stat": "courage",
        "diff": -2
      }
    ]
  }
}


{
  "title": "Treacherous Bog",
  "on_discover": {
    "description": "You enter a boggy marshland, immediately noticing the thick smog of mosquitos. With every step you take, a layer of dark sludge threatens to make you lose your balance or worse. You strain your eyes to keep your footing.",
    "stats": [
      {
        "stat": "vigor",
        "diff": -2
      }
    ]
  },
  "on_return": {
    "description": "You contemplate whether trekking through the bog was wise, as the marshland doesn't seem to release you without expending an incredible effort.",
    "stats": [
      {
        "stat": "vigor",
        "diff": -4
      }
    ]
  }
}

{
  "title": "Mysterious Cries",
  "on_discover": {
    "description": "You suddenly hear weird noises echoing through the trees. You can't tell what sort of creature is making the noises, but it sounds far too agitated for you to risk continuing your current path.",
    "stats": [
      {
        "stat": "courage",
        "diff": -2
      }
    ]
  },
  "on_return": {
    "description": "The cries are still sounding out. It's as if where ever you go they follow you or maybe even move around you.",
    "stats": [
      {
        "stat": "courage",
        "diff": -4
      }
    ]
  }
}

{
  "title": "Whispering Trees",
  "on_discover": {
    "description": "You come across a grove of old, gnarled trees. As the wind rustles through their leaves, you can swear you hear faint whispers carried on the breeze. It sends a shiver down your spine.",
    "stats": [
      {
        "stat": "courage",
        "diff": -1
      }
    ]
  },
  "on_return": {
    "description": "The grove of trees is still here, their whispered conversations growing louder. It makes you feel uneasy and on edge.",
    "stats": [
      {
        "stat": "courage",
        "diff": -2
      }
    ]
  }
}



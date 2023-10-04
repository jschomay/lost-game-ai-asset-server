# Generative AI pipeline for "Lost" infinite exploration game

This is the backend to my experimental AI game [Lost](https://github.com/jschomay/Lost) presented in the 2023 AI Engineer Summit (link coming soon).

This repo includes:

- code to fine tune a custom OpenAI LLM for scene generation
- a pipeline to generate scenes from this custom LLM and a fine tuned Leonardo.ai image model
- a generated scenes [preview server](https://lost-game-ai-assets-server.fly.dev/scenes)
- a cache and assert server for the game client

The game can be played at https://replit.com/@jschomay/Lost-forest-survival-game

## Fine-tuning

The original prompt used generate training data was:

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

The simplified prompt used in fine-tuning was:

    Help the user make up scenes for a game. The setting is being lost in a forest. Scenes have different feelings and involve various encounters.
    The output must follow a specific JSON map.  The only valid stats are `vigor` and `courage`.


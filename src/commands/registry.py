
from typing import TypedDict

class CommandConfig(TypedDict):
    raw_text: bool
    ignore_words: list[str]

#A dictionary containing all commands, where each command has a "tag" (raw_text). 
#If the tag is True, the command must be cleaned/filtered by the clear_target() function.
registry_commands: dict[str, CommandConfig]= {
    "OPEN_APP": {
        "raw_text": True,
        "ignore_words": ["open", "the", "launch", "start"]
    },
    "CLOSE_APP": {
        "raw_text": True,
        "ignore_words": ["close", "the", "quit", "exit"]
    },
    "SEARCH": {
        "raw_text": True,
        "ignore_words": ["search", "find", "look", "google", "in", "for", "web", "about"]
    },
    "ASK_GEMINI": {
        "raw_text": True,
        "ignore_words": ["one", "gemini", "ai"]
    },
    "VIEW_TASKS": {
        "raw_text": False,
        "ignore_words": []
    },
    "VIEW_SINGLE_TASK": {
        "raw_text": False,
        "ignore_words": []
    },
    "VIEW_HISTORY": {
        "raw_text": False,
        "ignore_words": []
    },
    "UPDATE_TASK":{
        "raw_text": False,
        "ignore_words": []
    },
    "DELETE_TASK": {
        "raw_text": False,
        "ignore_words": []
    },
    "ADD_TASK": {
        "raw_text": False,
        "ignore_words": []
    },
    "PLAY_MUSIC": {
        "raw_text": True,
        "ignore_words": ["play", "listen", "start", "music"]
    },
    "UPDATE": {
        "raw_text": False,
        "ignore_words": []
    },
    "NEXT_MUSIC": {
        "raw_text": False,
        "ignore_words": []
    },
    "STOP_MUSIC": {
        "raw_text": False,
        "ignore_words": []
    },
    "UP_VOL": {
        "raw_text": False,
        "ignore_words": []
    },
    "DOWN_VOL": {
        "raw_text": False,
        "ignore_words": []
    },
    "RESUME_MUSIC": {
        "raw_text": False,
        "ignore_words": []
    },

}
    

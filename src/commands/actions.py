
"""
This is where the link between identifying the command and executing the action occurs.
"""

import subprocess
import webbrowser
from database.methods import DbMethods, TaskState
from src.commands.apis import *
import urllib.parse
from src.audio.speech import *
from database.db import * 


class Actions:
    def __init__(self):
        self.db_m = DbMethods()
        create_table()
        self.router = {
            "VIEW_TASKS": self.view_task,
            "ADD_TASK": self.add_task,
            "VIEW_HISTORY": self.view_history,
            "OPEN_APP": self.open_app,
            "CLOSE_APP": self.close_app,
            "SEARCH": self.search,
            "ASK_GEMINI": self.ask_gemini,
            "PLAY_MUSIC": self.play_music,
            "UPDATE": self.update,
            "NEXT_MUSIC": self.next_music,
            "UP_VOL": self.up_vol,
            "DOWN_VOL": self.down_vol,
            "STOP_MUSIC": self.stop_music,
            "RESUME_MUSIC": self.resume_music,
            "DELETE_TASK": self.delete_task,
            "VIEW_SINGLE_TASK": self.view_unic_task,
        }

        
    def process(self, intent:str, target:str):
        if intent in self.router:
            action = self.router[intent]
            action(intent, target)

    def update_task(self, intent: str, target: str):
        task_name = ask_user("What is the name of the task you want to update?")
        
        if verify_task(task_name):
            new_name = None
            while True:
                new_name = ask_user("Say the new task name")
                if new_name == "skip":
                    new_name = task_name
                    break
                if verify_task(new_name):
                    speech("Task already exists")
                    continue
                    
                update_task_name(task_name, new_name) #old name, new name
                break

            while True:
                new_date = ask_user("Say the new task date")
                if new_date == "skip":
                    break

                formated_t = self.db_m.formatDate(new_date)

                if formated_t is not None:
                    update_task_time(new_name, formated_t)
                else:
                    speech("The new datetime is invalid")

            while True:
                status = ask_user("Say the new task status")
                if status == "skip":
                    break

                if TaskState(status):
                    # pending, finished, in progress
                    new_status = TaskState(status).value
                    update_task_status(new_name, new_status)
                    break

                else:
                    speech("Status not valid!")
                    continue
             
                    
    def view_unic_task(self, intent: str, target: str):
        task_name = ask_user("What is the name of the task you want to see?")
        view_single_task(task_name)

        _ = history_insert(intent, task_name)

    def delete_task(self, intent: str, target: str):
        task_name = ask_user("What is the name of the task you want to delete?")
        
        delete_task(task_name)
        speech(f"Task {task_name} deleted.")
        
        _ = history_insert(intent, task_name)
        
    def view_task(self, intent: str, target: str):
        view_tasks()
        _ = history_insert(intent, target)

    def add_task(self, intent: str, target: str):
        name = None
        formated_t = None
        description = None
        status = None

        while True:
            name = ask_user("What is the name of the task?")
    
            if not verify_task(name):
                break
            else:
                speech(f"A task with the name {name} already exists. Please choose a different name.")
                            
        while True:
            time_remaining = ask_user("What is the time remaining for the task?")
            if time_remaining == "skip":
                formated_t = None
                break

            formated_t = self.db_m.formatDate(time_remaining)

            if formated_t is not None:
                break
                
        while True:
            status = ask_user("What is the status of the task?")
            
            if status == "skip":
                status = None
                break
    
            if TaskState(status):
                # pending, finished, in progress
                status = TaskState(status).value 
                break

            else: 
                speech("Status not valid!")
                continue
         
        description = ask_user("What is the description of the task?")
        if description == "skip":
            description = None
            
        create_task(name, formated_t, status, description)
        speech(f"Task {name} created.")
        _ = history_insert(intent, name)

    def view_history(self, intent: str, target: str):
        history_query()
        speech("Showing history.")
        _ = history_insert(intent, target)

    def search(self, intent: str, target: str):
        formatted_content = urllib.parse.quote(target)
        url = f"https://www.google.com/search?q={formatted_content}"
        
        speech(f"Searching for {target}.")
        webbrowser.open(url)
        _ = history_insert(intent, target)

    def open_app(self, intent: str, target: str):
        try:      
           subprocess.Popen([target])
           _ = history_insert(intent, target)
           
        except Exception:
            speech(f"{target} not found.")
            
        else:
            speech(f"Opened {target}.")

    def close_app(self, intent: str, target: str):
        try:
            subprocess.Popen(["kill", target])
            _ = history_insert(intent, target)
            
        except Exception:
            speech(f"{target} not found!")
        else:
            speech(f"Closed {target}.")

    def ask_gemini(self, intent: str, target: str):
        speech("Thinking")

        response = ask_gemini(target)
        print(response)
        _ = history_insert(intent, target)

    def play_music(self, intent: str, target: str):
        subprocess.Popen(["spotify-launcher"])

        #Captures the "play music-name" command and searches for the specific song on Spotify
        #You need Spotify for Developers and spotify-launcher.
        try:
            if target:
                result = sp.search(q=target, limit= 1, type="track")

                if result:
                    tracks = result.get("tracks", {}).get("items", [])
    
                    if tracks:
                        music_uri = tracks[0]["uri"] #select the first track and your uri
                        sp.start_playback(uris = [music_uri])
                        speech(f"Playing {target}.")
                        _ = history_insert(intent, target)

                    else:
                        speech("Music not found!")
        except Exception:
            speech("Failed to communicate with Spotify")

    def update(self, intent: str, target: str):
        subprocess.Popen(["sudo", "pacman", "-Syu"])
        _ = history_insert(intent, target)
        speech("Update started.")

    def next_music(self, intent: str, target: str):
        subprocess.Popen(["playerctl", "next"])
        _ = history_insert(intent, target)

    def up_vol(self, intent: str, target: str):
        subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"])
        _ = history_insert(intent, target)

    def down_vol(self, intent: str, target: str):
        subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
        _ = history_insert(intent, target)

    def stop_music(self, intent: str, target: str):
        subprocess.Popen(["playerctl", "stop"])
        _ = history_insert(intent, target)

    def resume_music(self, intent: str, target: str):
        subprocess.Popen(["playerctl", "play"])
        _ = history_insert(intent, target)

    
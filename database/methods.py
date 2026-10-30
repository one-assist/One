from enum import StrEnum
from datetime import datetime
from dateparser.date import DateDataParser

"""
 A class to represent the state of a task.
 Inherits from struct.Struct to allow for easy serialization and deserialization.
"""
 
class TaskState (StrEnum):

    PENDING = "pending"
    FINISHED = "finished"
    IN_PROGRESS = "in progress"
    
class DbMethods:
    def __init__(self) -> None:
        # Store the current datetime for relative date parsing
        self.now: datetime = datetime.now()
        # Initialize the DateDataParser with the desired settings
        self.parser: DateDataParser = DateDataParser( 
            languages= ["en"], 
            settings= {
                "DATE_ORDER": "MDY",
                "RELATIVE_BASE": self.now, 
                "PREFER_DATES_FROM": "future"
        })
    
        
    def formatDate(self, text: str) -> datetime | None:        
        result = self.parser.get_date_data(text)

        return result.date_obj
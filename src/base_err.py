class OneError(Exception):
    
    def __init__(self, message: str, code: str = "ONE_ERROR"):
        self.message = message
        self.code = code

        super().__init__(f"{self.code}: {self.message}")
        
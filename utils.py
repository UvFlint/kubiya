class WeatherAppException(Exception):
    """Custom exception for the Weather App."""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

    def __str__(self):
        return f"{self.args[0]} (Error Code: {self.error_code})" if self.error_code else self.args[0]

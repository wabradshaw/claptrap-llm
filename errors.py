class ModelResponseFormatError(Exception):
    """Error raised when ChatGPT returns a response in a different format to what we expected.

    Attributes:
        model -- The GPT agent that was called
        response -- The response text from the agent
    """

    def __init__(self, model, response):
        self.model = model
        self.response = response
        super().__init__(f"""Model {model} did not return a response in the correct format. 
                         Received: {response}""")
        
class NoJokeFoundError(Exception):
    """Error raised when the system could not find any jokes that continue from the current point."""

class RetriableOpenAIError(Exception):
    """Error raised when OpenAI is unable to generate a response. We may be able to get a response in the next request."""

class PermanentOpenAIError(Exception):
    """Error raised when OpenAI is unable to generate a response. No further requests will help."""
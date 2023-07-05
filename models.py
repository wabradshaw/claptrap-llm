import os
import re
import logging

import openai

from errors import ModelResponseFormatError, RetriableOpenAIError, PermanentOpenAIError

# ChatCompletions
_GPT_3_5 = "gpt-3.5-turbo" 

# Patterns
_SOUND_ALIKE_PATTERN = re.compile("(?:\w+, )+\w+")
_SETUP_PATTERN = re.compile("(?<=SETUP:)(.*)\n?(?=PUNCHLINE:)")
_PUNCHLINE_PATTERN = re.compile("(?<=PUNCHLINE:)(.*)")

class Models:    
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def _completion(self, system, user, model=_GPT_3_5, temperature=1.0):
        messages = [{"role": "system", "content": system}]
        if user is not list: user = [user]
        for message in user:
            messages.append({"role": "user", "content": message})

        try:
            response = openai.ChatCompletion.create(            
                model=model,            
                temperature=temperature,
                messages=messages   
            )
            return response.choices[0].message.content
        except openai.error.APIError as e:
            logging.error("Open AI was unable to process a request")
            raise RetriableOpenAIError(e)
        except openai.error.Timeout as e:
            logging.error("Open AI request took too long")
            raise RetriableOpenAIError(e)
        except openai.error.RateLimitError as e:
            logging.critical("WE ARE MAKING TOO MANY REQUESTS!")
            raise PermanentOpenAIError(e)
        except openai.error.APIConnectionError as e:
            logging.critical("ISSUE WITH CONNECTION SETTINGS!")
            raise PermanentOpenAIError(e)
        except openai.error.InvalidRequestError as e:
            logging.critical("ISSUE WITH REQUEST SETUP!")
            raise PermanentOpenAIError(e)
        except openai.error.AuthenticationError as e:
            logging.critical("ISSUE WITH API KEY!")
            raise PermanentOpenAIError(e)
        except openai.error.ServiceUnavailableError as e:
            logging.error("Open AI could not handle the request")
            raise RetriableOpenAIError(e)
    
    def get_words_that_sound_like(self, word):
        _prompt = """
You are a poet's assistant. You generate options for words that either rhyme with or sound like other words.
Return a comma separated list of words. Do not say anything other than the list.

Examples: 
'wave' -> [knave, rave, waive, gave, save, wove]
'head' -> [red, led, sled, spread, bred, dread]"""        

        content = self._completion(
            system=_prompt,
            user=f"'{word}'"
        )
        matches = _SOUND_ALIKE_PATTERN.findall(content)

        if len(matches) == 1:
            return matches[0].split(", ")
        else:
            raise ModelResponseFormatError("SoundsLike", content)
        
    def get_words_that_sound_like_component(self, word, origin):
        _prompt = """
You are a poet's assistant. You generate options for words that either rhyme with or sound like other words.
Users will supply a candidate word, and a larger word or phrase containing that word. 
This should be used when the word could be pronounced in different ways.  
Return a comma separated list of words. Do not say anything other than the list.

Examples: 
'wave' from 'microwave' -> [knave, rave, waive, gave, save, wove]
'read' from 'bread' -> [red, led, sled, spread, bred, dread]
'read' from 'reading' -> [reed, feed, freed, reek, reap, lead, seed]"""        

        content = self._completion(
            system=_prompt,
            user=f"'{word}' from '{origin}'"
        )
        matches = _SOUND_ALIKE_PATTERN.findall(content)

        if len(matches) == 1:
            return matches[0].split(", ")
        else:
            raise ModelResponseFormatError("SoundsLikeComponent", content)

    def joke(self, punchline, origin, replacement):
        _prompt = """
You are a joke generation bot used to create simple puns. You tell jokes that ask what happens when you combine two things, and respond with a punchline that combines them as a punchline word. 

Users will supply three things:
P: The punchline word
O: The word it is based on
R: The part that was substituted in

Write a joke with a setup and a punchline.

The setup should reference O and S. The punchline should contain P.

E.g.
P: fight-mare, O: nightmare, R: fight ->
SETUP:What do you call a cross between a bad dream and a battle?
PUNCHLINE:A fightmare!

P: pup-cake, O: cupcake, R: pup ->
SETUP:What dog is made in a bakery?
PUNCHLINE:A pup-cake!"""        

        content = self._completion(
            system=_prompt,
            user=f"P:'{punchline}', O:'{origin}', R:'{replacement}'"
        )
        setup_matches = _SETUP_PATTERN.findall(content)
        punchline_matches = _PUNCHLINE_PATTERN.findall(content)

        if(len(setup_matches) == 1 and len(punchline_matches) == 1):
            return (setup_matches[0], punchline_matches[0])
        else:
            raise ModelResponseFormatError("Joke", content)
import os
import re

import openai

from errors import ModelResponseFormatError

# ChatCompletions
_GPT_3_5 = "gpt-3.5-turbo" 

# Patterns
_LONG_WORD_PATTERN = re.compile("(?:\w{8,}, ){9}\w{8,}")
_SOUND_ALIKE_PATTERN = re.compile("(?:\w+, )+\w+")
_SETUP_PATTERN = re.compile("(?<=SETUP:)(.*)\n?(?=PUNCHLINE:)")
_PUNCHLINE_PATTERN = re.compile("(?<=PUNCHLINE:)(.*)")

class Models:    
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_long_words_list(self):
        _prompt = """
You are a random word generator. You generate comma separated list of words with at least 8 characters in each. 
E.g. [cabbages, wonderful, believeable, completion, magnitude, participant, referenced, instructions, unavailable, tempests]"""
        
        response = openai.ChatCompletion.create(            
            model=_GPT_3_5,            
            temperature=1.0,
            messages=[
                {"role": "system", "content": _prompt},
                {"role": "user", "content": "Generate a list with 10 words. Do not say anything other than the list."}
            ]            
        )
        content = response.choices[0].message.content
        matches = _LONG_WORD_PATTERN.findall(content)
        
        if len(matches) == 1:
            return matches[0].split(", ")
        else:
            raise ModelResponseFormatError("LongWordsList", content)
    
    def get_words_that_sound_like(self, word, origin):
        _prompt = """
You are a poet's assistant. You generate options for words that either rhyme with or sound like other words.
Users will supply a candidate word, and a larger word or phrase containing that word. 
This should be used when the word could be pronounced in different ways.  
Return a comma separated list of words. Do not say anything other than the list.

Examples: 
'wave' from 'microwave' -> [knave, rave, waive, gave, save, wove]
'read' from 'bread' -> [red, led, sled, spread, bred, dread]
'read' from 'reading' -> [reed, feed, freed, reek, reap, lead, seed]"""        

        response = openai.ChatCompletion.create(            
            model=_GPT_3_5,            
            temperature=1.0,
            messages=[
                {"role": "system", "content": _prompt},
                {"role": "user", "content": f"'{word}' from '{origin}'"}
            ]            
        )
        content = response.choices[0].message.content
        matches = _SOUND_ALIKE_PATTERN.findall(content)

        if len(matches) == 1:
            return matches[0].split(", ")
        else:
            raise ModelResponseFormatError("SoundsLike", content)

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

        response = openai.ChatCompletion.create(            
            model=_GPT_3_5,            
            temperature=1.2,
            messages=[
                {"role": "system", "content": _prompt},
                {"role": "user", "content": f"P:'{punchline}', O:'{origin}', R:'{replacement}'"}
            ]            
        )
        content = response.choices[0].message.content
        setup_matches = _SETUP_PATTERN.findall(content)
        punchline_matches = _PUNCHLINE_PATTERN.findall(content)

        if(len(setup_matches) == 1 and len(punchline_matches) == 1):
            return (setup_matches[0], punchline_matches[0])
        else:
            raise ModelResponseFormatError("Joke", content)
import math
import random

from PyDictionary import PyDictionary

from models import Models
from errors import ModelResponseFormatError, NoJokeFoundError

class Joke():
    def __init__(self, setup, punchline, origin, component, replacement):
        self.setup = setup
        self.punchline = punchline
        self.origin = origin
        self.component = component
        self.replacement = replacement

class Services:
    # Used to remove particular constructions that lead to bad jokes.
    # Banned items are removed from the joke pool to avoid common poor pronunciation
    # Common items are removed to avoid recreating actual words
    _BANNED_PREFIXES = []
    _BANNED_SUFFIXES = ["ion"]    
    _COMMON_PREFIXES = ["un"]
    _COMMON_SUFFIXES = ["acy","al","dom","er","or","ism","ist","ity","ment",
                        "ing","s","es","ed","or"]

    def __init__(self):
        self._dictionary = PyDictionary()
        self._models = Models()

    def tell_joke(self):
        #TODO - Replace with internal candidate word list
        options = self._models.get_long_words_list()
        random.shuffle(options)

        for candidate in options:            
            try:
                return self.tell_joke_about(candidate)
            except (ModelResponseFormatError, NoJokeFoundError):
                # We'll try again so long as there's another possible option. 
                # Other exceptions are raised as normal.
                print(f"No results for {candidate}")
                pass

        raise NoJokeFoundError()
                
    def tell_joke_about(self, phrase):
        candidate_words = self._get_constituent_words(phrase)

        for candidate in candidate_words:

            replacement_substrings = self._models.get_words_that_sound_like(word=candidate,origin=phrase)

            for candidate_replacement in replacement_substrings:
                substitution = self._get_substitution(origin=phrase, 
                                component=candidate, 
                                replacement=candidate_replacement)

                (setup, punchline) = self._models.joke(punchline=substitution,
                                                       origin=phrase, 
                                                       replacement=candidate_replacement)

                response = Joke(setup=setup,
                                punchline=punchline,
                                origin=phrase, 
                                component=candidate, 
                                replacement=candidate_replacement
                                )
                return response
    
        raise NoJokeFoundError()
    
    def _get_constituent_words(self, origin):
            # Max sub-word length is either 6 characters, 
            # or half the word + 1 characters. 
            # E.g. 5 letters for an 8/9 letter word. 6 for 10/11. 
            valid_affix_limits = range(3,min(7,2+math.floor(len(origin)/2)))
            candidate_prefixes = [origin[:n] for n in valid_affix_limits 
                                  if origin[:n] not in self._BANNED_PREFIXES 
                                  and origin[n:] not in self._COMMON_SUFFIXES]
            candidate_suffixes = [origin[-n:] for n in valid_affix_limits 
                                  if origin[-n:] not in self._BANNED_SUFFIXES
                                  and origin[-n:] not in self._COMMON_PREFIXES]
            
            candidate_affixes = set(candidate_prefixes)
            candidate_affixes.update(candidate_suffixes)

            #TODO - Replace with an internal word list to avoid processing time and remove obscure words
            candidate_words = [word for word in candidate_affixes 
                               if self._dictionary.meaning(word, True)]            
            
            return candidate_words
    
    def _get_substitution(self, origin, component, replacement):
        if(origin.startswith(component)):
            return replacement + '-' + origin[len(component):]
        else:
            return origin[:-len(component)] + "-" + replacement
        

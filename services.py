import math
import random
import logging

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
    _BANNED_SUFFIXES = ["ion","ing"]    
    _COMMON_PREFIXES = ["un"]
    _COMMON_SUFFIXES = ["acy","al","dom","er","or","ism","ist","ity","ment",
                        "ing","s","es","ed","or"]

    def __init__(self):
        self._models = Models()
        self._short_words = set(self._load_words('res/short'))
        self._long_words = self._load_words('res/long')

    def _load_words(self, path):
        with open(path, 'r') as file:
            file_content = file.read()

        words = file_content.split('\n')
        words = [word.strip() for word in words]
        return words

    def tell_joke(self):
        options = random.choices(population=self._long_words,k=10)

        logging.debug(f"Possible joke words: {options}")

        for candidate in options:            
            try:
                return self.tell_joke_about(candidate)
            except (ModelResponseFormatError, NoJokeFoundError):
                # We'll try again so long as there's another possible option. 
                # Other exceptions are raised as normal.
                logging.info(f"Could not think of a joke for {candidate}")
                pass

        raise NoJokeFoundError()
                
    def tell_joke_about(self, phrase):
        logging.info(f"Trying to create a joke about [{phrase}]")

        candidate_words = self._get_constituent_words(phrase)

        if not candidate_words:
            logging.info(f"The phrase [{phrase}] could not be broken up")
            raise NoJokeFoundError()
        
        logging.debug(f"Possible candidates for [{phrase}]: [{candidate_words}]")
        for candidate in candidate_words:
            logging.debug(f"Trying to create a joke about the [{candidate}] in [{phrase}]")

            replacement_substrings = self._models.get_words_that_sound_like(word=candidate,origin=phrase)
            random.shuffle(replacement_substrings)

            if not replacement_substrings:
                logging.info(f"No replacements found for the [{candidate}] in [{phrase}]")
            else:
                candidate_replacement = replacement_substrings[0]
                logging.debug(f"Trying to replace the [{candidate}] in [{phrase}] with [{candidate_replacement}]")

                substitution = self._get_substitution(origin=phrase, 
                                component=candidate, 
                                replacement=candidate_replacement)

                (setup, punchline) = self._models.joke(punchline=substitution,
                                                       origin=phrase, 
                                                       replacement=candidate_replacement)

                logging.debug(f"Joke for [{phrase}] returned as [{punchline}]")

                response = Joke(setup=setup,
                                punchline=punchline,
                                origin=phrase, 
                                component=candidate, 
                                replacement=candidate_replacement
                                )
                return response
    
        logging.info(f"No replacements found for any subsection of [{phrase}]")
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

            candidate_words = [word for word in candidate_affixes 
                               if word in self._short_words]
            
            return candidate_words
    
    def _get_substitution(self, origin, component, replacement):
        if(origin.startswith(component)):
            return replacement + '-' + origin[len(component):]
        else:
            return origin[:-len(component)] + "-" + replacement
        

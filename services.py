import logging
import math
import random

import config as config
from dictionary import Dictionary
from models import Models
from errors import * 

#TODO - Move to a general settings config and update the message that goes to the user.
MAX_TOPIC_LENGTH = 16

class Joke:
    """
    A simple wrapper class for basic jokes and the logic constructing them.
    
    Attributes:
    setup        -- The first line of the joke.
    punchline    -- The supposedly funny part of the joke.
    nucleus      -- The phrase that was converted into a punchline. Referenced in the setup.
    component    -- Part of the nucleus that will be changed. Not present in the joke, only implied.
    change       -- The word replacing a component of the nucleus. Referenced in the setup.
    substitution -- The result of inserting the component into the nucleus. Used for the punchline. 
    """

    def __init__(self, setup, punchline, nucleus, component, change, substitution):
        """
        Define the joke.

        Arguments:
        setup        -- The first line of the joke.
        punchline    -- The supposedly funny part of the joke.
        nucleus      -- The phrase that was converted into a punchline. Referenced in the setup.
        component    -- Part of the nucleus that will be changed. Not present in the joke, only implied.
        change       -- The word replacing a component of the nucleus. Referenced in the setup.
        substitution -- The result of inserting the component into the nucleus. Used for the punchline. 
        """

        self.setup = setup
        self.punchline = punchline
        self.nucleus = nucleus
        self.component = component
        self.change = change
        self.substitution = substitution

class Services:
    # Used to remove particular constructions that lead to bad jokes.
    # Banned items are removed from the joke pool to avoid common poor pronunciation
    # Common items are removed to avoid recreating actual words
    _BANNED_PREFIXES = []
    _BANNED_SUFFIXES = ["ion","ing"]    
    _COMMON_PREFIXES = ["un"]
    _COMMON_SUFFIXES = ["acy","al","dom","er","or","ism","ist","ity","ment",
                        "ing","s","es","ed","or"]
    
    _BLOCKLIST = config.load_words('res/blocklist')

    def __init__(self):
        self._models = Models()
        self._dictionary = Dictionary()

    def tell_joke(self):
        """
        Attempts to tell a brand new joke about anything.

        The idea here is to find a random phrase to use as the nucleus for a joke.
        The nucleus must start or end with another word (called the component).
        A new word that sounds like that component will be chosen (the change).
        This change will be substituted into the nucleus to make the 
        substitution, which will become the punchline. AI is then used to 
        produce the setup and punchline for a joke that uses these parts.

        For example:
        What type of dog is made in a bakery?
        A pup-cake!

        In this example, cupcake is the nucleus that starts the joke. Cup is 
        chosen as the component (cake could also have been used). The word pup
        is then picked as the change, which becomes the substitution pup-cake.  
        """
        
        logging.info("Generating a joke from scratch")
        options = self._dictionary.get_random_phrases(10)

        logging.debug(f"Possible nucleii: {options}")

        for candidate_nucleus in options:            
            try:
                return self._tell_joke_about_nucleus(candidate_nucleus)
            except (ModelResponseFormatError, NoJokeFoundError):
                # We'll try again so long as there's another possible option. 
                # Other exceptions are raised as normal.
                logging.info(f"Could not think of a joke for {candidate_nucleus}")
                pass

        raise NoJokeFoundError()

    def tell_joke_about(self, topic):
        logging.info(f"Generating a joke about {topic}")

        topic = topic.lower()

        self._verify_appropriate_topic(topic)

        joke_types = []

        if len(topic) <= 7:
            joke_types.append("change")
            joke_types.append("component")
        
        if len(topic) >= 6:
            joke_types.append("phrase")

        random.shuffle(joke_types)
        joke_types.append("topic")

        for joke_type in joke_types:
            try:                                
                match joke_type:
                    case "phrase":
                        return self._tell_joke_about_nucleus(topic)
                    case "change":
                        return self._tell_joke_about_change(topic)
                    case "component":
                        return self._tell_joke_about_component(topic)
                        raise NoJokeFoundError
                    case "topic":
                        #TODO - Topic based jokes
                        raise NoJokeFoundError
                    
            except (ModelResponseFormatError, NoJokeFoundError):
                logging.info(f"Could not think of a joke for {topic} as a {joke_type}")
                pass

        raise NoJokeFoundError()
    
    def _tell_joke_about_change(self, change):
        logging.info(f"Trying to create a joke for change [{change}]")

        candidate_components = self._models.get_words_that_sound_like(word=change)

        if not candidate_components:
            logging.info(f"The change [{change}] does not sound like anything")
            raise NoJokeFoundError()
        
        logging.debug(f"Possible components for [{change}]: [{candidate_components}]")
        for candidate_component in candidate_components:
            logging.debug(f"Trying to create a joke where [{candidate_component}] becomes [{change}]")

            candidate_nucleii = self._dictionary.some_phrases_starting_with(candidate_component)
            
            if not candidate_nucleii:
                logging.debug(f"No nucleii found starting with [{candidate_component}] for [{change}]")
            else:
                random.shuffle(candidate_nucleii)
                nucleus = candidate_nucleii[0]
                logging.debug(f"Trying to joke about [{change}] where it is subbed into [{nucleus}]")
            
                substitution = self._get_substitution(nucleus=nucleus, 
                                                      component=candidate_component, 
                                                      change=change)
                
                return self._put_joke_together(nucleus=nucleus, 
                                               component=candidate_component,
                                               change=change,
                                               substitution=substitution)
        raise NoJokeFoundError()
    
    def _tell_joke_about_component(self, component):
        logging.info(f"Trying to create a joke for component [{component}]")

        candidate_nucleii = self._dictionary.some_phrases_starting_with(component)

        if not candidate_nucleii:
            logging.debug(f"No nucleii found starting with [{component}]")
            raise NoJokeFoundError()        
        else:  
            logging.debug(f"Possible nucleii for [{component}]: [{candidate_nucleii}]")
            random.shuffle(candidate_nucleii)
            nucleus = candidate_nucleii[0]
            logging.debug(f"Trying to joke about the [{component}] in [{nucleus}]")

            candidate_changes = self._models.get_words_that_sound_like(word=component)

            if not candidate_changes:
                logging.info(f"The component [{component}] does not sound like anything")
                raise NoJokeFoundError()
            else:
                logging.debug(f"Possible changes for [{component}]: [{candidate_changes}]")
                random.shuffle(candidate_changes)
                change = candidate_changes[0]
                logging.debug(f"Trying to create a joke where [{component}] becomes [{change}]")

                substitution = self._get_substitution(nucleus=nucleus, 
                                                      component=component, 
                                                      change=change)
                
                return self._put_joke_together(nucleus=nucleus, 
                                               component=component,
                                               change=change,
                                               substitution=substitution)
    
    def _tell_joke_about_nucleus(self, nucleus):
        """
        Attempt to tell a joke using the supplied nucleus. The nucleus will 
        be turned into a pun and used as a punchline.        
        """

        logging.info(f"Trying to create a joke about the nucleus [{nucleus}]")

        candidate_components = self._get_constituent_words(nucleus)

        if not candidate_components:
            logging.info(f"The nucleus [{nucleus}] could not be broken up")
            raise NoJokeFoundError()
        
        logging.debug(f"Possible components for [{nucleus}]: [{candidate_components}]")

        for candidate_component in candidate_components:
            logging.debug(f"Trying to create a joke about the [{candidate_component}] in [{nucleus}]")

            possible_changes = self._models.get_words_that_sound_like_component(
                component=candidate_component,
                context=nucleus
            )

            if not possible_changes:
                logging.info(f"No replacements found for the [{candidate_component}] in [{nucleus}]")
            else:
                random.shuffle(possible_changes)
                change = possible_changes[0]
                logging.debug(f"Trying to replace the [{candidate_component}] in [{nucleus}] with [{change}]")

                substitution = self._get_substitution(nucleus=nucleus, 
                                component=candidate_component, 
                                change=change)

                return self._put_joke_together(nucleus=nucleus, 
                                               component=candidate_component, 
                                               change=change,
                                               substitution=substitution)
    
        logging.info(f"No substitutions found for any components of [{nucleus}]")
        raise NoJokeFoundError()

    def _put_joke_together(self, nucleus, component, change, substitution):
        """Requests a setup and punchline for the given joke and wraps it as a Joke object"""

        (setup, punchline) = self._models.joke(punchline=substitution,
                                               original=nucleus,
                                               change=change)

        logging.debug(f"Joke for [{nucleus}] returned as [{punchline}]")

        response = Joke(setup=setup,
                        punchline=punchline,
                        nucleus=nucleus,
                        component=component,
                        change=change, 
                        substitution=substitution)
        return response
    
    def _get_substitution(self, nucleus, component, change):
        """
        Replaces the component in a nucleus with a change, separated with a 
        hyphen. 
        
        Only designed for the start and end of the nucleus. This is to avoid 
        making replacements midword, or double replacements. 

        E.g.
        catapult, cat, bat -> bat-apult
        amalgam, am, um -> um-algam
        banana, na, pa -> bana-pa
        """

        if(nucleus.startswith(component)):
            return change + '-' + nucleus[len(component):]
        else:
            return nucleus[:-len(component)] + "-" + change
        
    def _get_constituent_words(self, phrase):
        """
        Find the list of words that the input either starts or ends with. 

        Finds constituents where the rest of the phrase is long enough to be 
        recognisable. Practically, that means avoiding selecting too much of the
        phrase. The rule in use is half the word length + 1, or a max of 6 chars.
        
        Certain constituents are excluded as they often lead to poor jokes. This
        includes banned suffixes like 'ion' that sound very different as stand
        alone words. It also prevents constituents where the rest of the word is
        common, like leaving 'ing'.  

        Arguments:
        phrase -- A long word to break into constituent words.
        """

        # E.g. 5 letters for an 8/9 letter word. 6 for 10/11. 
        valid_affix_limits = range(3,min(7,2+math.floor(len(phrase)/2)))

        candidate_prefixes = [phrase[:n] for n in valid_affix_limits 
                                if phrase[:n] not in self._BANNED_PREFIXES 
                                and phrase[n:] not in self._COMMON_SUFFIXES]
        candidate_suffixes = [phrase[-n:] for n in valid_affix_limits 
                                if phrase[-n:] not in self._BANNED_SUFFIXES
                                and phrase[-n:] not in self._COMMON_PREFIXES]
        
        candidate_affixes = set(candidate_prefixes)
        candidate_affixes.update(candidate_suffixes)

        candidate_words = [word for word in candidate_affixes 
                            if self._dictionary.word_exists(word)]
        
        return candidate_words
    
    def _verify_appropriate_topic(self, topic):
        """
        Makes sure that an input topic is of a reasonable size, and isn't about
        anything that we can't joke about. Raises an exception if there's an 
        issue.
        """
        if not topic or len(topic.strip()) == 0:
            logging.error(f"User requested an empty topic, possible client issue")
            raise MissingTopicError
        
        if len(topic) > MAX_TOPIC_LENGTH:
            logging.error(f"User requested {topic} which is too long, possible client issue")
            raise LongTopicError(topic)
                
        if topic in self._BLOCKLIST or topic[:-1] in self._BLOCKLIST:
            logging.debug(f"User requested {topic} which is on the blocklist")
            raise InappropriateTopicError(topic)
        
        if self._models.is_invalid_input(topic):
            logging.error(f"User requested {topic}, add it to the blocklist")
            raise InappropriateTopicError(topic)
        
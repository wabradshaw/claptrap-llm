import random

import config as config

class Dictionary:
    def __init__(self):
        #TODO - Move res paths to config
        self._words = set(config.load_words('res/short'))
        self._phrases = config.load_words('res/long')
        self._phrase_count = len(self._phrases)

    def get_random_phrases(self, count=10):
        return random.choices(population=self._phrases, k=count)
    
    def word_exists(self, word):
        return word in self._words
    
    def some_phrases_starting_with(self, word):
        word_length = len(word)
        start = 0
        end = self._phrase_count - 1

        # Using an initial random midpoint as some words e.g. 'con' are common.
        mid = random.randint(start, end) 

        while start <= end:
            candidate = self._phrases[mid][:word_length]
            if candidate == word:
                window_start = max(start, mid-10)
                window_end = min(end, mid+10)
                return [self._phrases[index] 
                        for index in range(window_start, window_end)
                        if word == self._phrases[index][:word_length]]
            elif word < candidate:
                end = mid - 1        
            else:
                start = mid + 1                

            mid = (start + end) // 2
        return []

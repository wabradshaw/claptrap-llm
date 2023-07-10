def load_words(path):
    """
    Load a resource file full of words into a list. 
    The words should be separated by new lines.

    Arguments:
    path -- The location of the words file.
    """
    with open(path, 'r') as file:
        file_content = file.read()

    words = file_content.split('\n')
    words = [word.strip() for word in words]
    return words
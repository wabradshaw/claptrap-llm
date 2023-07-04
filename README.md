# Claptrap V2

A joke telling AI that frequently misses the mark. It combines a basic understanding of pun construction with the power of large language models, resulting in some nightmarish jokes. 

Jokes like:
What do you call a tiny piece of matter that initiates something?
A start-icle!

Sorry. Comedians aren't in danger of losing their jobs. The system believes that particle sounds like start-icle, and then attempts to build a joke for that punchline.

## Thanks

1. [OpenAI](https://platform.openai.com/) - This version of Claptrap uses OpenAI to generate the jokes. This project was forked from https://beta.openai.com/docs/quickstart. 
2. [The google-10000-english project](https://github.com/first20hours/google-10000-english) - A list of 10,000 words that was used as the basis for the dictionary.
3. Kim Binsted, Graeme Ritchie and Helen Pain - Their work on [JAPE (Joking Analysis and Production Engine)](http://www2.hawaii.edu/~binsted/papers/Binstedthesis.pdf), [STANDUP](https://homepages.abdn.ac.uk/g.ritchie/pages/papers/IEEE_IS_2006.pdf) and the [Joking Computer](http://joking.abdn.ac.uk/home.shtml) served as the basis for this design. In particular Helen was my advisor in my first foray into computational humour. She introduced me to the system, gave me the opportunity to work with it, then put up with months of me complaining about the quality of the jokes. Thanks also to [the teams behind STANDUP and the Joking Computer](http://joking.abdn.ac.uk/people7.shtml), it might have been Kim & Graeme's brainchild, but it wouldn't have got where it did without all of the researchers in Edinburgh, Aberdeen & Dundee.

## Setup

1. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

2. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

3. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

4. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

5. Run the app:

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)
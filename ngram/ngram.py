import random
from collections import defaultdict

class NGram:
    def __init__(self, n: int):
        self.n = n
        # Will count the occurances of context, n - 1 words appearing before the n-th word
        self.context_count = defaultdict(int)

        # Will count the occurances of words after contexts
        self.word_after_context_count = defaultdict(lambda: defaultdict(int))

    def train(self, tokenized_text: list):
        # Add n-1 starting tags to allow for generation of the first 
        # n - 1 words without having n - 1 tokens as context
        starting_tags = ["<START>"] * (self.n - 1)
        end_tag = ["<END>"]
        tokenized_text = starting_tags + tokenized_text + end_tag

        num_n_grams = len(tokenized_text) - self.n + 1
        for i in range(num_n_grams):
            # get the n - 1 gram starting from index i for the denominator of MLE
            context = tuple(tokenized_text[i:i + self.n - 1])

            # track count of context occurance (n - 1 gram)
            self.context_count[context] += 1

            # track count of word occuring after context (n-th word in n-gram)
            self.word_after_context_count[context][tokenized_text[i + self.n - 1]] += 1

    def conditional_probalilty(self, word: str, context: tuple):
        # Compute probability of word given context/history using MLE
        try:
            return self.word_after_context_count[context][word] / self.context_count[context]
        except ZeroDivisionError:
            return 0

    def get_next_token(self, context):
        # Get all tokens which appear after context
        possible_words = self.word_after_context_count[context]

        # Sort possible words that follow context by occurances in descending order
        possible_words = dict(sorted(possible_words.items(), key=lambda item: item[1], reverse=True))

        # Get the total occurances of all possible words to generate a random index
        total_occurances_of_possible_words = sum(list(possible_words.values()))

        # Generate a random index to select a word
        rand_idx = random.randint(0, total_occurances_of_possible_words - 1)

        # Generate a list where each possible word is repeated in the list based on the number of times in occurs in word_after_context_count
        # i.e. select random possible word weighted by occurances
        selection_list = list()
        for token, occurances in possible_words.items():
            selection_list.extend([token] * occurances)
        
        # Return randomly selected word
        return selection_list[rand_idx]


        '''
        Below is a alterative strategy which just picks the most occuring word.
        The problem is that for a set n value, the lyrics generated do not change
        with each run.
        '''
        # Get the max number of occurances that a word appears after the context
        # max_occurances = list(possible_words.values())[0]

        # # Get all words with the max_occurance
        # possible_words = [token for token in possible_words.keys() if possible_words[token] == max_occurances]

        # # Pick a word randomly to break any ties
        # return possible_words[random.randint(0, len(possible_words) - 1)]

    def generate_text(self, num_words: int = -1):
        # Create starting tags
        text = ["<START>"] * (self.n - 1)
        i = 0

        # if num_words == 1, then we will generate until <END> is generated
        while num_words == -1 or i < num_words:
            next_word = self.get_next_token(tuple(text[i:i + self.n - 1])) # Generate next most probable word
            text.append(next_word)

            if next_word == "<END>":
                break
            i += 1 
        
        # Remove starting and ending tags
        text = [word for word in text if word != "<START>" and word != "<END>"]

        # Create string from list
        return " ".join(text)

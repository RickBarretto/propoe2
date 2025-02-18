from dataclasses import dataclass
import random

from src.model.rhyme import Rhyme
from src.model.score import Score
from src.model.poem_evaluation import Evaluation
from src.model.utils import remove_end_ponctuation
import sys


@dataclass
class PoemBuilder:
    """

    Attributes
    ----------
    sentences: dict[str, Rhyme]
        List of Rhyme objects
    rhyme: str
        Rhyme Pattern. E.g.: "AABB CCDD"
    metrics: list[int]
        List of metrics per verse
    poem: str
        maps score name and its weight
    score_weight: dict[str, float]
        Score Weight for the poem evaluation
    evaluation: Evaluation
        The evaluation of the Poem
    orig_stdout: TextIO
        The original System's Stdout
    f: TextIOWrapper[_WrappedBuffer]
        The file reference for the filename with "write" access.
    """

    sentences: dict[str, Rhyme]
    metrics: list[int]
    rhyme: str
    score_weight: dict[str, float]
    _filename: str
    _seed: int | None

    def __post_init__(self):
        self.poem: str = ""
        self.evaluation: Evaluation = Evaluation()
        random.seed(self._seed)

        self.orig_stdout = sys.stdout
        self.f = open(self._filename, "w")
        sys.stdout = self.f

    def result(self) -> None:
        print(self.poem)
        print(self.evaluation)

    def save(self, path) -> None:
        """Save poem in txt file."""
        text_file = open(path, "w")
        text_file.write(self.poem)
        text_file.close()

    def build(self) -> None:
        """Build poem. Get best sentences and add it in the string self.poem."""
        sentences = self.get_poem_sentences()
        for letter in self.rhyme:
            if letter == " ":
                self.poem = self.poem + "\n"
            else:
                s = sentences[letter].pop(0)
                self.poem = (
                    self.poem
                    + remove_end_ponctuation(s.sentence).capitalize()
                    + "\n"
                )
        sys.stdout = self.orig_stdout
        self.f.close()

    def random_sentence(self, letter, sentences, metric_count):
        pos_sentences = self.sentences[letter].metrics[
            self.metrics[metric_count]
        ]
        number = random.randrange(len(pos_sentences))
        s = pos_sentences[number]
        if s.not_in(sentences[letter]):
            return s
        else:
            return self.random_sentence(letter, sentences, metric_count)

    def random_verse(self, sentence):
        number = random.randrange(len(sentence.verse_structures))
        return sentence.verse_structures[number]

    def initialize_sentences(self):
        """Initializa a Dict mapping the letters from the rhyme pattern to an empty list."""
        sentences = {}
        for letter in self.sentences:
            sentences[letter] = []
        return sentences

    def get_poem_sentences(self):
        """Return a list of Sentence objects in order to build a poem."""
        rhyme = self.rhyme
        sentences = self.initialize_sentences()
        # Dict that maps letters from rhyme pattern to its last Rhyme object
        last_rhyme = {}
        new_strophe = True
        # Index from self.metrics that shows with metric does this Sentence object needs.
        metric_count = 0
        # Iterate through every letter from rhyme pattern, one by one, in order.
        for letter in rhyme:
            if letter == " ":
                new_strophe = True
            elif new_strophe:
                current = self.random_sentence(letter, sentences, metric_count)
                sentences[letter].append(current)
                current_verse = self.random_verse(current)
                # Reference verse.
                fixed_verse = current_verse
                last_rhyme[letter] = current_verse
                print(current_verse.scanned_sentence)
                print()
                new_strophe = False
                metric_count += 1
            else:
                # If not a new rhyme, if there is a verse we can compare to.
                if letter in last_rhyme:
                    # Last Verse object that rhymes with the new verse to be found.
                    verse_rhyme = last_rhyme[letter]
                else:
                    verse_rhyme = None
                next_s, next_verse = self.find_sentence(
                    sentences,
                    [current_verse, fixed_verse],
                    letter,
                    verse_rhyme,
                    metric_count,
                )

                last_rhyme[letter] = next_verse
                sentences[letter].append(next_s)
                current = next_s
                current_verse = next_verse
                metric_count += 1

        return sentences

    # TODO: define missing types
    def find_sentence(
        self,
        sentences,
        verses: list,
        letter: str,
        last_rhyme,
        metric_count,
    ):
        """Return best Sentence object given a score.

        Parameters:
          sentences: List of Sentence objects chosen for the current poem.
          verses: List with only the first Verse object of strophe and the current Verse object.
          letter: Which rhyme pattern it is. EX: "A", "B" or "C".
          last_rhyme: Verse object of the last Sentence that rhymes.
          metric_count: Index from self.metrics that shows with metric does
            this Sentence object needs.

        Return:
          next_s: Chosen Sentence object
          next_verse: Chosen Verse object from the Sentence object
        """
        max_score = -1
        count = 0
        for sentence in self.sentences[letter].metrics[
            self.metrics[metric_count]
        ]:
            if sentence.not_in(sentences[letter]):
                for possible_verse in sentence.verse_structures:
                    score = Score(possible_verse.scanned_sentence)
                    count += 1
                    print("------------------")
                    for verse in verses:
                        score.score(
                            verse, possible_verse, last_rhyme, self.score_weight
                        )

                        print(score)
                        print()
                        if score.score_result > max_score:
                            max_score = score.score_result
                            next_s = sentence
                            next_verse = possible_verse
                            result_score = score
        print("------------ESCOLHIDO----------------")
        print("Quantidade de versos:", str(count))
        # TODO: ``result_score`` may never be assigned
        print(result_score)
        print()

        self.evaluation.add(result_score)
        # TODO: ``next_s`` and ``next_verse`` may never be assigned
        return next_s, next_verse

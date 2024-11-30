from typing import Protocol
from pydantic import BaseModel

from src.model.poem_evaluation import Evaluation as DomainEvaluation

__all__ = ["Poem"]


class IsPoem(Protocol):
    @property
    def content(self) -> str: ...

    @property
    def evaluation(self) -> DomainEvaluation: ...

class RhymeScore(BaseModel):
    structure: float
    internal: float
    consonant: float


class EvaluationScore(BaseModel):
    accent: float
    stress: float
    rhymes: RhymeScore
    result: float


class Evaluation(BaseModel):
    scores: EvaluationScore

    @staticmethod
    def from_domain(evaluation: DomainEvaluation) -> "Evaluation":
        schema_score = EvaluationScore(
            accent=evaluation.accent_score,
            stress=evaluation.stress_score,
            result=evaluation.score_result,
            rhymes=RhymeScore(
                structure=evaluation.rhyme_structure_score,
                internal=evaluation.intern_rhyme_score,
                consonant=evaluation.consonant_rhyme_score,
            ),
        )

        return Evaluation(scores=schema_score)


class Poem(BaseModel):
    content: list[str]
    evaluation: Evaluation

    @staticmethod
    def from_domain(poem: IsPoem) -> "Poem":
        return Poem(
            content=poem.content.splitlines(),
            evaluation=Evaluation.from_domain(poem.evaluation),
        )

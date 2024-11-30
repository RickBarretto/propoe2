from typing import Protocol
from pydantic import BaseModel

from src.model.poem_evaluation import Evaluation as DomainEvaluation

__all__ = ["Poem"]


class IsPoem(Protocol):
    @property
    def content(self) -> str: ...

    @property
    def evaluation(self) -> DomainEvaluation: ...


class EvaluationScore(BaseModel):
    vocal_harmony: float
    accentuation: float
    tonic_position: float
    internal_rhyme: float
    rhythmic_structure: float


class Evaluation(BaseModel):
    scores: EvaluationScore
    score: float

    @staticmethod
    def from_domain(model: DomainEvaluation) -> "Evaluation":
        schema_score = EvaluationScore(
            accentuation=model.accent_score,
            internal_rhyme=model.intern_rhyme_score,
            rhythmic_structure=model.rhyme_structure_score,
            tonic_position=model.stress_score,
            vocal_harmony=model.consonant_rhyme_score
        )

        return Evaluation(scores=schema_score, score=model.score_result)


class Poem(BaseModel):
    content: list[str]
    evaluation: Evaluation

    @staticmethod
    def from_domain(poem: IsPoem) -> "Poem":
        return Poem(
            content=poem.content.splitlines(),
            evaluation=Evaluation.from_domain(poem.evaluation),
        )

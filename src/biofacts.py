"""
BioFacts DB — Evidence-Based Biological Facts
Stub minimal para imports del modulo.
Autor: Fernando Fondillo — VIHOLABS / BioFish AI
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class RecommendationGrade(str, Enum):
    STRONG_FOR = "STRONG FOR"
    WEAK_FOR = "WEAK FOR"
    NEUTRAL = "NEUTRAL"
    WEAK_AGAINST = "WEAK AGAINST"
    STRONG_AGAINST = "STRONG AGAINST"


@dataclass
class BioFact:
    id: str = ""
    category: str = ""
    mechanism: str = ""
    fact: str = ""
    evidence_level: EvidenceLevel = EvidenceLevel.C
    recommendation: RecommendationGrade = RecommendationGrade.NEUTRAL
    source_paper: str = ""
    year: int = 2020
    population: str = ""
    effect_size: Optional[str] = None
    caveats: Optional[str] = None


class BioFactsDB:

    def __init__(self):
        self._facts: Dict[str, List[BioFact]] = {}

    def get_facts(self, category: str) -> List[BioFact]:
        return self._facts.get(category, [])

    def get_all_categories(self) -> List[str]:
        return list(self._facts.keys())

    def get_facts_by_level(self, level: EvidenceLevel) -> List[BioFact]:
        results = []
        for facts in self._facts.values():
            results.extend([f for f in facts if f.evidence_level == level])
        return results


db = BioFactsDB()
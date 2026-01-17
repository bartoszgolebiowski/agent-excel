from __future__ import annotations

"""Skill definitions used by the research workflow."""

from .models import AnalyzeAndPlanSkillOutput, AnalyzeEmailSkillOutput
from .base import SkillDefinition, SkillName


ANALYZE_AND_PLAN_SKILL = SkillDefinition(
    name=SkillName.ANALYZE_AND_PLAN,
    template_name="skills/analyze_and_plan.j2",
    output_model=AnalyzeAndPlanSkillOutput,
)

ANALYZE_EMAIL_SKILL = SkillDefinition(
    name=SkillName.ANALYZE_EMAIL,
    template_name="skills/analyze_email.j2",
    output_model=AnalyzeEmailSkillOutput,
)

ALL_SKILLS = [
    ANALYZE_AND_PLAN_SKILL,
    ANALYZE_EMAIL_SKILL,
]

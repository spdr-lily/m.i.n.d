from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.base import AssessmentScale, ScaleQuestion
from app.ml.assessment_scales import get_scale, SCALES_REGISTRY, ScaleDefinition
from app.schemas.assessment import AssessmentRequest, AssessmentResult


def score_assessment(request: AssessmentRequest) -> AssessmentResult:
    scale_def = get_scale(request.scale_name)
    if not scale_def:
        raise ValueError(f"Unknown scale: {request.scale_name}")

    values = [r.response_value for r in request.responses]
    total = scale_def.score(values)
    severity, interpretation = scale_def.interpret(total)

    return AssessmentResult(
        scale_name=scale_def.name,
        scale_description=scale_def.description,
        total_score=total,
        severity=severity,
        interpretation=interpretation,
        responses=request.responses,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def get_scales_list() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}


def get_seeded_scale_data(db: Session) -> Dict[str, int]:
    scales: Dict[str, int] = {}
    for name, scale_def in SCALES_REGISTRY.items():
        existing = db.query(AssessmentScale).filter(
            AssessmentScale.scale_name == name
        ).first()
        if existing:
            scale_id = existing.scale_id
        else:
            scale = AssessmentScale(scale_name=name, scale_description=scale_def.description)
            db.add(scale)
            db.flush()
            scale_id = scale.scale_id
            for i, q_text in enumerate(scale_def.questions, start=1):
                db.add(ScaleQuestion(scale_id=scale_id, question_text=q_text, question_order=i))
            db.flush()
        scales[name] = scale_id
    db.commit()
    return scales

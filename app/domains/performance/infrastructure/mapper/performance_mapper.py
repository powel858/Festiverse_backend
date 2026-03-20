import json

from app.domains.performance.domain.entity.performance import Performance
from app.domains.performance.infrastructure.orm.performance_model import PerformanceModel


class PerformanceMapper:

    @staticmethod
    def to_entity(model: PerformanceModel) -> Performance:
        styurls: list[str] = []
        if model.styurls_json:
            try:
                styurls = json.loads(model.styurls_json)
            except (json.JSONDecodeError, TypeError):
                styurls = []

        relates: list[dict[str, str]] = []
        if model.relates_json:
            try:
                relates = json.loads(model.relates_json)
            except (json.JSONDecodeError, TypeError):
                relates = []

        return Performance(
            mt20id=model.mt20id,
            prfnm=model.prfnm,
            prfpdfrom=model.prfpdfrom,
            prfpdto=model.prfpdto,
            fcltynm=model.fcltynm,
            prfcast=model.prfcast,
            prfcrew=model.prfcrew,
            prfruntime=model.prfruntime,
            prfage=model.prfage,
            pcseguidance=model.pcseguidance,
            poster=model.poster,
            genrenm=model.genrenm,
            prfstate=model.prfstate,
            openrun=model.openrun,
            styurls=styurls,
            relates=relates,
            dtguidance=model.dtguidance,
            area=model.area,
            mt10id=model.mt10id,
            festival=model.festival,
            sty=model.sty,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Performance) -> PerformanceModel:
        return PerformanceModel(
            mt20id=entity.mt20id,
            prfnm=entity.prfnm,
            prfpdfrom=entity.prfpdfrom,
            prfpdto=entity.prfpdto,
            fcltynm=entity.fcltynm,
            prfcast=entity.prfcast,
            prfcrew=entity.prfcrew,
            prfruntime=entity.prfruntime,
            prfage=entity.prfage,
            pcseguidance=entity.pcseguidance,
            poster=entity.poster,
            genrenm=entity.genrenm,
            prfstate=entity.prfstate,
            openrun=entity.openrun,
            styurls_json=json.dumps(entity.styurls, ensure_ascii=False),
            relates_json=json.dumps(entity.relates, ensure_ascii=False),
            dtguidance=entity.dtguidance,
            area=entity.area,
            mt10id=entity.mt10id,
            festival=entity.festival,
            sty=entity.sty,
            updated_at=entity.updated_at,
        )

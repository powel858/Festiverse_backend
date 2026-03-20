from app.domains.performance.domain.entity.venue import Venue
from app.domains.performance.infrastructure.orm.venue_model import VenueModel


class VenueMapper:

    @staticmethod
    def to_entity(model: VenueModel) -> Venue:
        return Venue(
            mt10id=model.mt10id,
            fcltynm=model.fcltynm,
            mt13cnt=model.mt13cnt,
            fcltychartr=model.fcltychartr,
            opende=model.opende,
            seatscale=model.seatscale,
            telno=model.telno,
            relateurl=model.relateurl,
            adres=model.adres,
            la=model.la,
            lo=model.lo,
            parkinglot=model.parkinglot,
            restaurant=model.restaurant,
            cafe=model.cafe,
            store=model.store,
            nolibang=model.nolibang,
            suyu=model.suyu,
            disability=model.disability,
        )

    @staticmethod
    def to_model(entity: Venue) -> VenueModel:
        return VenueModel(
            mt10id=entity.mt10id,
            fcltynm=entity.fcltynm,
            mt13cnt=entity.mt13cnt,
            fcltychartr=entity.fcltychartr,
            opende=entity.opende,
            seatscale=entity.seatscale,
            telno=entity.telno,
            relateurl=entity.relateurl,
            adres=entity.adres,
            la=entity.la,
            lo=entity.lo,
            parkinglot=entity.parkinglot,
            restaurant=entity.restaurant,
            cafe=entity.cafe,
            store=entity.store,
            nolibang=entity.nolibang,
            suyu=entity.suyu,
            disability=entity.disability,
        )

import datetime, random, sys
sys.path.append('../')

from app import db
from app.models import *

def gen_outlettypes():
    db.session.add(
        OutletType(
            maintype = 'premium',
        )
    )
    db.session.add(
        OutletType(
            maintype = 'star',
        )
    )
    db.session.add(
        OutletType(
            maintype = 'smile',
        )
    )
    db.session.add(
        OutletType(
            maintype = 'smartfren gadget outlet',
        )
    )
    db.session.add(
        OutletType(
            maintype = 'regular',
        )
    )
    db.session.commit()

def main():
    #start_date = datetime.date(2013, 10, 1)
    #end_date = datetime.date(2013, 10, 30)

    facility_ids = list(zip(*db.session.query(Facility.id).all())[0])
    outlettype_ids = list(zip(*db.session.query(OutletType.id).all())[0]) 

    # Populate non-smile type facilities
    for fid in facility_ids:
        print 'Adding Type for Fac: %s'%fid
        toadd = FacilityOutletTypeMapping(
            facility_id = fid,
            outlettype_id = random.choice(outlettype_ids),
        )

        db.session.add(toadd)

    # Commit
    db.session.commit()

gen_outlettypes()
main()

import datetime, random, sys
sys.path.append('../')

from app import db
from app.models import *

def gen_subtypes():
    db.session.add(
        RegularOutletSubtype(
            subtype = 'super platinum'
        )
    )
    db.session.add(
        RegularOutletSubtype(
            subtype = 'platinum'
        )
    )
    db.session.add(
        RegularOutletSubtype(
            subtype = 'gold'
        )
    )
    db.session.add(
        RegularOutletSubtype(
            subtype = 'silver'
        )
    )

    db.session.commit()

def daily():
    start_date = datetime.date(2013, 10, 1)
    end_date = datetime.date(2013, 10, 30)

    boundary_ids = list(zip(*db.session.query(Boundary.id).all())[0])
    product_ids = list(zip(*db.session.query(Product.id).all())[0])
    subtype_ids = list(zip(*db.session.query(RegularOutletSubtype.id).all())[0]) 

    for b in boundary_ids:
        print 'Adding for boundary id: %s'%b
        t = start_date
        while (t <= end_date):
            for p in product_ids:
                db.session.add(
                    BoundaryProductDailySubtype(
                        boundary_id = b,
                        product_id = p,
                        regular_outlet_subtype_id = subtype_ids[random.randint(0, len(subtype_ids) - 1)],
                        date = t,
                        outletCount = random.randint(0, 100),
                        activation = random.randint(0, 1000)
                    )
                )
            t += datetime.timedelta(days=1)
        db.session.commit()

def monthly():
    month = 10
    year = 2013

    boundary_ids = list(zip(*db.session.query(Boundary.id).all())[0])
    product_ids = list(zip(*db.session.query(Product.id).all())[0])
    subtype_ids = list(zip(*db.session.query(RegularOutletSubtype.id).all())[0]) 

    for b in boundary_ids:
        print 'Adding for boundary id: %s'%b
        for p in product_ids:
            db.session.add(
                BoundaryProductMonthlySubtype(
                    boundary_id = b,
                    product_id = p,
                    regular_outlet_subtype_id = subtype_ids[random.randint(0, len(subtype_ids) - 1)],
                    month = month,
                    year = year,
                    outletCount = random.randint(0, 100),
                    activation = random.randint(0, 1000)
                )
            )
        db.session.commit()

def yearly():
    year = 2013

    boundary_ids = list(zip(*db.session.query(Boundary.id).all())[0])
    product_ids = list(zip(*db.session.query(Product.id).all())[0])
    subtype_ids = list(zip(*db.session.query(RegularOutletSubtype.id).all())[0]) 

    for b in boundary_ids:
        print 'Adding for boundary id: %s'%b
        for p in product_ids:
            db.session.add(
                BoundaryProductYearlySubtype(
                    boundary_id = b,
                    product_id = p,
                    regular_outlet_subtype_id = subtype_ids[random.randint(0, len(subtype_ids) - 1)],
                    year = year,
                    outletCount = random.randint(0, 100),
                    activation = random.randint(0, 1000)
                )
            )
        db.session.commit()

def weekly():
    weeks = [
        (datetime.date(2013,10,03), datetime.date(2013,10,9)),
        (datetime.date(2013,10,24), datetime.date(2013,10,30)),
        (datetime.date(2013,10,10), datetime.date(2013,10,16)),
        (datetime.date(2013,10,17), datetime.date(2013,10,23)),
        (datetime.date(2013,9,26), datetime.date(2013,10,2)),
    ]

    boundary_ids = list(zip(*db.session.query(Boundary.id).all())[0])
    product_ids = list(zip(*db.session.query(Product.id).all())[0])
    subtype_ids = list(zip(*db.session.query(RegularOutletSubtype.id).all())[0]) 

    for b in boundary_ids:
        print 'Adding for boundary id: %s'%b
        for w in weeks:
            for p in product_ids:
                db.session.add(
                    BoundaryProductWeeklySubtype(
                        boundary_id = b,
                        product_id = p,
                        regular_outlet_subtype_id = subtype_ids[random.randint(0, len(subtype_ids) - 1)],
                        start_week_date = w[0],
                        end_week_date = w[1],
                        outletCount = random.randint(0, 100),
                        activation = random.randint(0, 1000)
                    )
                )
        db.session.commit()

gen_subtypes()
daily()
monthly()
yearly()
weekly()

import random, sys
sys.path.append('../')

from app import db
from app.models import *


# Only creating fake owner information for Aceh facilities
def main():
    # Create schema for name and address
    name_schema = FacilitySchema(
        column_name = 'owner_name',
        data_type = 1
    )

    address_schema = FacilitySchema(
        column_name = 'owner_address',
        data_type = 1
    )

    db.session.add(name_schema)
    db.session.add(address_schema)
    db.session.commit()

    facilities = [1, 2, 95, 96, 97, 98, 99, 100, 101, 102, 103, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 635, 636]
    names = ['Rachman', 'Salim', 'Sanjaya', 'Santoso', 'Sasmita', 'Setiabudi', 'Setiawan', 'Sudirman', 'Sudjarwadi', 'Sugiarto', 'Sumadi', 'Susanto', 'Susman', 'Sutedja', 'Tan', 'Tanudjaja', 'Tanuwidjaja', 'Tedja', 'Tedjo', 'Wibowo', 'Widjaja', 'Yuwono']
    addresses = ['Signature Tower Jakarta', 'Pertamina Energy Tower', 'Cemindo Tower', 'Lippo St.Moritz', 'Wisma 46', 'Ciputra World Hotel', 'Menara BCA', 'Equity Tower', 'Ciputra World Apartment', 'The Peak Twin Towers', 'Graha Energi', 'Bakrie Tower', 'Kempinski Residences', 'The Pinnacle Jakarta', 'Ritz-Carlton Jakarta', 'The Grand Hyatt Residence', 'The Plaza Tower', 'The Icon Residences', 'Central Park Residence', 'Wisma Mulia', 'Residence 8 @ Senopati', 'UOB Plaza', 'Central Park Office Tower', 'Fx Plaza Sudirman', 'ITC Kuningan', 'Pacific Place', 'Central Park Office Tower', 'Aston Veranda', 'Indofood Tower & The Mayflower Marriott Executive Residence', 'Menara Kadin Indonesia', 'The Peak Twin Towers 2', 'Amartapura 1', 'Batam City Condominium', 'Bliss Tower Hotels & Residences']

    for f in facilities:
        db.session.add(
            FacilityCustomData(
                schema_id = name_schema.id,
                facility_id = f,
                data = '%s %s'%(names[random.randint(0, len(names))], names[random.randint(0, len(names))]),
            )
        )

        db.session.add(
            FacilityCustomData(
                schema_id = address_schema.id,
                facility_id = f,
                data = '#%s-%s, %s, Indonesia(%s)'%(random.randint(0, 100), random.randint(0, 100), addresses[random.randint(0, len(addresses))], random.randint(10000, 99999)),
            )
        )
    db.session.commit()

main()

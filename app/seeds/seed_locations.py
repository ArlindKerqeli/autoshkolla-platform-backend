"""
Seed Kosovo geographic reference data.
Run with: flask seed-locations
"""
import click
from flask.cli import with_appcontext
from app.utils.db import db
from app.models.country_model import Country
from app.models.municipality_model import Municipality
from app.models.place_model import Place


# Kosovo municipalities with codes
KOSOVO_MUNICIPALITIES = [
    (1, 'Deçan'), (2, 'Dragash'), (3, 'Ferizaj'), (4, 'Fushë Kosovë'),
    (5, 'Gjakovë'), (6, 'Gjilan'), (7, 'Gllogoc'), (8, 'Graçanicë'),
    (9, 'Hani i Elezit'), (10, 'Istog'), (11, 'Junik'), (12, 'Kaçanik'),
    (13, 'Kamenicë'), (14, 'Klinë'), (15, 'Kllokot'), (16, 'Leposaviq'),
    (17, 'Lipjan'), (18, 'Malishevë'), (19, 'Mamushë'), (20, 'Mitrovicë e Jugut'),
    (21, 'Mitrovicë e Veriut'), (22, 'Novobërdë'), (23, 'Obiliq'),
    (24, 'Partesh'), (25, 'Pejë'), (26, 'Podujevë'), (27, 'Prishtinë'),
    (28, 'Prizren'), (29, 'Rahovec'), (30, 'Ranillug'), (31, 'Shtërpcë'),
    (32, 'Shtime'), (33, 'Skenderaj'), (34, 'Suharekë'), (35, 'Viti'),
    (36, 'Vushtrri'), (37, 'Zubin Potok'), (38, 'Zveçan'),
]

# Major places per municipality (selection of most important cities/villages)
# Format: (municipality_code, place_code, place_name)
KOSOVO_PLACES = [
    # Ferizaj municipality (code 3) - primary for demo
    (3, 200, 'Ferizaj'), (3, 201, 'Babush i Muhaxherëve'), (3, 202, 'Bablak'),
    (3, 203, 'Bibaj'), (3, 204, 'Brod'), (3, 205, 'Dardani'),
    (3, 206, 'Gërlicë'), (3, 207, 'Greme'), (3, 208, 'Jezerc'),
    (3, 209, 'Komogllavë'), (3, 210, 'Nerodime e Epërme'), (3, 211, 'Nerodime e Poshtme'),
    (3, 212, 'Nikadin'), (3, 213, 'Papaz'), (3, 214, 'Prelez'),
    (3, 215, 'Racak'), (3, 216, 'Softaj'), (3, 217, 'Talinovc i Muhaxherëve'),
    (3, 218, 'Zaskok'),
    # Prishtinë municipality (code 27)
    (27, 300, 'Prishtinë'), (27, 301, 'Çagllavicë'), (27, 302, 'Hajvali'),
    (27, 303, 'Graçanicë'), (27, 304, 'Keqekollë'), (27, 305, 'Matiçan'),
    (27, 306, 'Obiliq'), (27, 307, 'Bërnicë e Poshtme'), (27, 308, 'Bërnicë e Epërme'),
    # Prizren municipality (code 28)
    (28, 400, 'Prizren'), (28, 401, 'Lubizhdë'), (28, 402, 'Mushtishtë'),
    (28, 403, 'Piranë'), (28, 404, 'Zhur'), (28, 405, 'Landovicë'),
    # Gjilan municipality (code 6)
    (6, 500, 'Gjilan'), (6, 501, 'Cërnicë'), (6, 502, 'Livoç i Epërm'),
    (6, 503, 'Malishevë'), (6, 504, 'Ponesh'), (6, 505, 'Shillovë'),
    # Pejë municipality (code 25)
    (25, 600, 'Pejë'), (25, 601, 'Baran'), (25, 602, 'Brestovik'),
    (25, 603, 'Gorazhdec'), (25, 604, 'Leshan'), (25, 605, 'Vitomiricë'),
    # Gjakovë municipality (code 5)
    (5, 700, 'Gjakovë'), (5, 701, 'Meja'), (5, 702, 'Ponoshec'),
    (5, 703, 'Rogovë'), (5, 704, 'Skivjan'),
    # Mitrovicë e Jugut (code 20)
    (20, 800, 'Mitrovicë'), (20, 801, 'Banjskë'), (20, 802, 'Vushtrri'),
    # Vushtrri (code 36)
    (36, 900, 'Vushtrri'), (36, 901, 'Nedakovc'), (36, 902, 'Smrekonicë'),
    # Podujevë (code 26)
    (26, 1000, 'Podujevë'), (26, 1001, 'Bradash'), (26, 1002, 'Llapashticë'),
    # Lipjan (code 17)
    (17, 1100, 'Lipjan'), (17, 1101, 'Magure'), (17, 1102, 'Rufc'),
    # Suharekë (code 34)
    (34, 1200, 'Suharekë'), (34, 1201, 'Gelancë'), (34, 1202, 'Studençan'),
    # Kaçanik (code 12)
    (12, 1300, 'Kaçanik'), (12, 1301, 'Brezovicë'), (12, 1302, 'Elezhan'),
    # Rahovec (code 29)
    (29, 1400, 'Rahovec'), (29, 1401, 'Hoçë e Madhe'), (29, 1402, 'Krusha e Madhe'),
    # Shtime (code 32)
    (32, 1500, 'Shtime'), (32, 1501, 'Carrallevë'), (32, 1502, 'Muzeqinë'),
    # Skenderaj (code 33)
    (33, 1600, 'Skenderaj'), (33, 1601, 'Klinë e Epërme'), (33, 1602, 'Prekaz'),
    # Klinë (code 14)
    (14, 1700, 'Klinë'), (14, 1701, 'Budisalc'), (14, 1702, 'Dollc'),
    # Istog (code 10)
    (10, 1800, 'Istog'), (10, 1801, 'Banja e Pejës'), (10, 1802, 'Gurrakoc'),
    # Malishevë (code 18)
    (18, 1900, 'Malishevë'), (18, 1901, 'Dragobil'), (18, 1902, 'Kijevë'),
    # Deçan (code 1)
    (1, 2000, 'Deçan'), (1, 2001, 'Isniq'), (1, 2002, 'Loxhë'),
    # Viti (code 35)
    (35, 2100, 'Viti'), (35, 2101, 'Pozheran'), (35, 2102, 'Stubëll e Epërme'),
    # Dragash (code 2)
    (2, 2200, 'Dragash'), (2, 2201, 'Brod'), (2, 2202, 'Krushevë'),
    # Fushë Kosovë (code 4)
    (4, 2300, 'Fushë Kosovë'), (4, 2301, 'Miradi e Epërme'), (4, 2302, 'Sllatinë'),
    # Hani i Elezit (code 9)
    (9, 2400, 'Hani i Elezit'), (9, 2401, 'Neçë'),
    # Kamenicë (code 13)
    (13, 2500, 'Kamenicë'), (13, 2501, 'Rogaçicë'), (13, 2502, 'Strezoc'),
]


def register_seed_commands(app):
    """Register seed CLI commands."""

    @app.cli.command('seed-locations')
    @with_appcontext
    def seed_locations():
        """Seed Kosovo geographic reference data."""
        click.echo('Seeding location data...')

        # Create countries
        kosovo = Country.query.filter_by(code='KS').first()
        if not kosovo:
            kosovo = Country(name='Kosovë', code='KS')
            db.session.add(kosovo)
            click.echo('  Created country: Kosovë')

        other = Country.query.filter_by(code='OTHER').first()
        if not other:
            other = Country(name='Jashtë Kosovës', code='OTHER')
            db.session.add(other)
            click.echo('  Created country: Jashtë Kosovës')

        db.session.flush()

        # Create municipalities
        muni_map = {}
        for code, name in KOSOVO_MUNICIPALITIES:
            existing = Municipality.query.filter_by(code=code).first()
            if not existing:
                muni = Municipality(country_id=kosovo.id, name=name, code=code)
                db.session.add(muni)
                muni_map[code] = muni
                click.echo(f'  Created municipality: {name}')
            else:
                muni_map[code] = existing

        db.session.flush()

        # Create places
        place_count = 0
        for muni_code, place_code, place_name in KOSOVO_PLACES:
            existing = Place.query.filter_by(code=place_code).first()
            if not existing and muni_code in muni_map:
                place = Place(
                    municipality_id=muni_map[muni_code].id,
                    name=place_name,
                    code=place_code
                )
                db.session.add(place)
                place_count += 1

        db.session.commit()
        click.echo(f'  Created {place_count} places')
        click.echo('Location seed complete!')

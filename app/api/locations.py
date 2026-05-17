from flask import request
from app.api import api_bp
from app.models.country_model import Country
from app.models.municipality_model import Municipality
from app.models.place_model import Place


@api_bp.get('/locations/countries')
def get_countries():
    """Fetch all countries."""
    countries = Country.query.order_by(Country.name).all()
    return [c.to_dict() for c in countries]


@api_bp.get('/locations/municipalities')
def get_municipalities():
    """Fetch municipalities, optionally filtered by country_id."""
    country_id = request.args.get('country_id')
    query = Municipality.query
    if country_id:
        query = query.filter_by(country_id=country_id)
    municipalities = query.order_by(Municipality.name).all()
    return [m.to_dict() for m in municipalities]


@api_bp.get('/locations/places')
def get_places():
    """Fetch places, optionally filtered by municipality_id."""
    municipality_id = request.args.get('municipality_id')
    query = Place.query
    if municipality_id:
        query = query.filter_by(municipality_id=municipality_id)
    places = query.order_by(Place.name).all()
    return [p.to_dict() for p in places]

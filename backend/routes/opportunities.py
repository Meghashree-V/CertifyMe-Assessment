from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from backend.extensions import db
from backend.models import Opportunity

opp_bp = Blueprint('opportunities', __name__, url_prefix='/api/opportunities')


def opp_to_dict(o):
    """Serialize an Opportunity to a dict."""
    return {
        'id': o.id,
        'name': o.name,
        'category': o.category,
        'duration': o.duration,
        'start_date': o.start_date,
        'description': o.description,
        'skills': o.skills,
        'future_opportunities': o.future_opportunities,
        'max_applicants': o.max_applicants,
        'created_at': o.created_at.isoformat() if o.created_at else None,
    }


# ---------- US-2.1: GET all opportunities for logged-in admin ----------
@opp_bp.route('', methods=['GET'])
@login_required
def get_opportunities():
    opps = Opportunity.query.filter_by(admin_id=current_user.id)\
                            .order_by(Opportunity.created_at.desc()).all()
    return jsonify([opp_to_dict(o) for o in opps]), 200


# ---------- US-2.2: CREATE a new opportunity ----------
@opp_bp.route('', methods=['POST'])
@login_required
def create_opportunity():
    data = request.get_json()

    name = (data.get('name') or '').strip()
    duration = (data.get('duration') or '').strip()
    start_date = (data.get('start_date') or '').strip()
    description = (data.get('description') or '').strip()
    skills = (data.get('skills') or '').strip()
    category = (data.get('category') or '').strip()
    future_opportunities = (data.get('future_opportunities') or '').strip()
    max_applicants = data.get('max_applicants') or None

    # Validate required fields
    errors = {}
    if not name:
        errors['name'] = 'Opportunity name is required'
    if not duration:
        errors['duration'] = 'Duration is required'
    if not start_date:
        errors['start_date'] = 'Start date is required'
    if not description:
        errors['description'] = 'Description is required'
    if not skills:
        errors['skills'] = 'Skills are required'
    if not category:
        errors['category'] = 'Category is required'
    if not future_opportunities:
        errors['future_opportunities'] = 'Future opportunities field is required'

    if errors:
        return jsonify({'errors': errors}), 400

    opp = Opportunity(
        admin_id=current_user.id,
        name=name,
        duration=duration,
        start_date=start_date,
        description=description,
        skills=skills,
        category=category,
        future_opportunities=future_opportunities,
        max_applicants=int(max_applicants) if max_applicants else None
    )
    db.session.add(opp)
    db.session.commit()

    return jsonify(opp_to_dict(opp)), 201


# ---------- US-2.5: UPDATE an opportunity ----------
@opp_bp.route('/<string:opp_id>', methods=['PUT'])
@login_required
def update_opportunity(opp_id):
    opp = Opportunity.query.filter_by(id=opp_id, admin_id=current_user.id).first()
    if not opp:
        return jsonify({'error': 'Opportunity not found or access denied'}), 404

    data = request.get_json() or {}

    opp.name = (data.get('name') or opp.name).strip()
    opp.duration = (data.get('duration') or opp.duration).strip()
    opp.start_date = (data.get('start_date') or opp.start_date).strip()
    opp.description = (data.get('description') or opp.description).strip()
    opp.skills = (data.get('skills') or opp.skills).strip()
    opp.category = (data.get('category') or opp.category).strip()
    opp.future_opportunities = (data.get('future_opportunities') or opp.future_opportunities).strip()
    opp.max_applicants = int(data['max_applicants']) if data.get('max_applicants') else opp.max_applicants

    db.session.commit()
    return jsonify(opp_to_dict(opp)), 200


# ---------- US-2.6: DELETE an opportunity ----------
@opp_bp.route('/<string:opp_id>', methods=['DELETE'])
@login_required
def delete_opportunity(opp_id):
    opp = Opportunity.query.filter_by(id=opp_id, admin_id=current_user.id).first()
    if not opp:
        return jsonify({'error': 'Opportunity not found or access denied'}), 404

    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted successfully'}), 200

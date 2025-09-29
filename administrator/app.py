from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emergency_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session expires after 2 hours

# Enable CORS for cross-origin requests
CORS(app)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # admin, spoc, responder, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # fire, flood, earthquake, trapped, other
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    building_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='open')  # open, acknowledged, assigned, resolved, false_alarm
    severity = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_incidents')
    responder = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_incidents')

class Checkin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # safe, stuck, unknown
    location = db.Column(db.String(200))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='checkins')
    incident = db.relationship('Incident', backref='checkins')

class Drill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    drill_type = db.Column(db.String(50))  # fire, earthquake, flood, evacuation
    location = db.Column(db.String(200), default='IGDTUW Campus')
    scheduled_date = db.Column(db.DateTime)
    file_url = db.Column(db.String(200))
    score = db.Column(db.Float, default=0.0)
    participation_count = db.Column(db.Integer, default=0)
    total_expected = db.Column(db.Integer, default=100)
    conducted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    conductor = db.relationship('User', backref='conducted_drills')

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100))
    role = db.Column(db.String(50))  # NDRF, police, fire, ambulance, hospital
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    region = db.Column(db.String(100))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20))  # alert, warning, info, drill
    severity = db.Column(db.String(10), default='medium')
    target_roles = db.Column(db.String(100))  # comma-separated roles
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    class_name = db.Column('class', db.String(20), nullable=False)  # Grade 1-12
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_phone = db.Column(db.String(20), nullable=False)
    medical_conditions = db.Column(db.Text)
    drill_participation = db.Column(db.Integer, default=0)  # Percentage
    last_checkin = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentDrillParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drill_id = db.Column(db.Integer, db.ForeignKey('drill.id'), nullable=False)
    participated = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    participated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='drill_participations')
    drill = db.relationship('Drill', backref='student_participations')

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'spoc']:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session.permanent = True  # Enable session timeout
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login_new.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Get statistics
    total_incidents = Incident.query.count()
    active_incidents = Incident.query.filter(Incident.status.in_(['open', 'acknowledged', 'assigned'])).count()
    safe_checkins = Checkin.query.filter_by(status='safe').count()
    stuck_checkins = Checkin.query.filter_by(status='stuck').count()
    
    # Get recent incidents
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    
    # Get recent notifications
    recent_notifications = Notification.query.filter_by(is_active=True).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Calculate preparedness score (mock calculation)
    total_drills = Drill.query.count()
    avg_participation = db.session.query(db.func.avg(Drill.score)).scalar() or 0
    preparedness_score = min(100, (total_drills * 10) + (avg_participation * 0.5))
    
    stats = {
        'total_incidents': total_incidents,
        'active_incidents': active_incidents,
        'safe_checkins': safe_checkins,
        'stuck_checkins': stuck_checkins,
        'preparedness_score': round(preparedness_score, 1)
    }
    
    return render_template('dashboard_new.html', 
                         user=user, 
                         stats=stats, 
                         recent_incidents=recent_incidents,
                         recent_notifications=recent_notifications)

@app.route('/incidents')
@login_required
def incidents():
    page = request.args.get('page', 1, type=int)
    incident_type = request.args.get('type', '')
    status = request.args.get('status', '')
    
    query = Incident.query
    
    if incident_type:
        query = query.filter_by(type=incident_type)
    if status:
        query = query.filter_by(status=status)
    
    incidents = query.order_by(Incident.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('incidents_new.html', incidents=incidents)

@app.route('/incident/<int:id>')
@login_required
def incident_detail(id):
    incident = Incident.query.get_or_404(id)
    checkins = Checkin.query.filter_by(incident_id=id).all()
    return render_template('incident_detail.html', incident=incident, checkins=checkins)

@app.route('/create_incident', methods=['GET', 'POST'])
@login_required
def create_incident():
    if request.method == 'POST':
        incident = Incident(
            reporter_id=session['user_id'],
            type=request.form['type'],
            description=request.form['description'],
            location=request.form['location'],
            building_id=request.form.get('building_id', ''),
            severity=request.form.get('severity', 'medium')
        )
        
        # Handle coordinates if provided
        if request.form.get('latitude') and request.form.get('longitude'):
            incident.latitude = float(request.form['latitude'])
            incident.longitude = float(request.form['longitude'])
        
        db.session.add(incident)
        db.session.commit()
        
        flash('Incident reported successfully!', 'success')
        return redirect(url_for('incidents'))
    
    return render_template('create_incident_new.html')

@app.route('/drills')
@login_required
def drills():
    drills = Drill.query.order_by(Drill.created_at.desc()).all()
    return render_template('drills_new.html', drills=drills)

@app.route('/create_drill', methods=['GET', 'POST'])
@login_required
@admin_required
def create_drill():
    if request.method == 'POST':
        # Parse scheduled date
        scheduled_date = None
        if request.form.get('scheduled_date'):
            try:
                scheduled_date = datetime.strptime(request.form['scheduled_date'], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    scheduled_date = datetime.strptime(request.form['scheduled_date'], '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DDTHH:MM format.', 'error')
                    return render_template('create_drill.html')
        
        # Create drill with basic fields first
        drill_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'drill_type': request.form['drill_type'],
            'total_expected': int(request.form.get('total_expected', 100)),
            'conducted_by': session['user_id']
        }
        
        # Add new fields if they exist in the model
        if hasattr(Drill, 'location'):
            drill_data['location'] = request.form.get('location', 'IGDTUW Campus')
        
        if hasattr(Drill, 'scheduled_date') and scheduled_date:
            drill_data['scheduled_date'] = scheduled_date
        
        drill = Drill(**drill_data)
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                drill.file_url = f'uploads/{filename}'
        
        db.session.add(drill)
        db.session.commit()
        
        flash('Drill created successfully!', 'success')
        return redirect(url_for('drills'))
    
    return render_template('create_drill.html')

@app.route('/attendance')
@login_required
def attendance():
    checkins = Checkin.query.order_by(Checkin.created_at.desc()).all()
    
    # Group by status
    safe_count = len([c for c in checkins if c.status == 'safe'])
    stuck_count = len([c for c in checkins if c.status == 'stuck'])
    unknown_count = len([c for c in checkins if c.status == 'unknown'])
    
    stats = {
        'safe': safe_count,
        'stuck': stuck_count,
        'unknown': unknown_count,
        'total': len(checkins)
    }
    
    return render_template('attendance_new.html', checkins=checkins, stats=stats)

@app.route('/checkin', methods=['POST'])
@login_required
def checkin():
    status = request.form['status']
    incident_id = request.form.get('incident_id')
    location = request.form.get('location', '')
    message = request.form.get('message', '')
    
    checkin = Checkin(
        user_id=session['user_id'],
        incident_id=incident_id if incident_id else None,
        status=status,
        location=location,
        message=message
    )
    
    db.session.add(checkin)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Check-in recorded successfully'})

@app.route('/emergency_contacts')
@login_required
def emergency_contacts():
    contacts = EmergencyContact.query.filter_by(is_active=True).order_by(EmergencyContact.role, EmergencyContact.name).all()
    return render_template('emergency_contacts_new.html', contacts=contacts)

@app.route('/create_contact', methods=['GET', 'POST'])
@login_required
@admin_required
def create_contact():
    if request.method == 'POST':
        contact = EmergencyContact(
            name=request.form['name'],
            organization=request.form['organization'],
            role=request.form['role'],
            phone=request.form['phone'],
            email=request.form.get('email', ''),
            region=request.form['region'],
            address=request.form.get('address', '')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Emergency contact added successfully!', 'success')
        return redirect(url_for('emergency_contacts'))
    
    return render_template('create_contact_new.html')

@app.route('/analytics')
@login_required
@admin_required
def analytics():
    # Incident analytics
    incident_types = db.session.query(Incident.type, db.func.count(Incident.id)).group_by(Incident.type).all()
    incident_status = db.session.query(Incident.status, db.func.count(Incident.id)).group_by(Incident.status).all()
    
    # Monthly incident trends
    monthly_incidents = db.session.query(
        db.func.strftime('%Y-%m', Incident.created_at).label('month'),
        db.func.count(Incident.id).label('count')
    ).group_by('month').order_by('month').all()
    
    # Drill effectiveness
    drill_stats = db.session.query(
        Drill.drill_type,
        db.func.avg(Drill.score).label('avg_score'),
        db.func.count(Drill.id).label('total_drills')
    ).group_by(Drill.drill_type).all()
    
    analytics_data = {
        'incident_types': dict(incident_types),
        'incident_status': dict(incident_status),
        'monthly_incidents': [{'month': m, 'count': c} for m, c in monthly_incidents],
        'drill_stats': [{'type': d[0], 'avg_score': round(d[1] or 0, 2), 'total': d[2]} for d in drill_stats]
    }
    
    return render_template('analytics.html', analytics=analytics_data)

# API Endpoints
@app.route('/api/incidents', methods=['GET', 'POST'])
@login_required
def api_incidents():
    if request.method == 'POST':
        data = request.get_json()
        incident = Incident(
            reporter_id=session['user_id'],
            type=data['type'],
            description=data['description'],
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            building_id=data.get('building_id', ''),
            severity=data.get('severity', 'medium')
        )
        db.session.add(incident)
        db.session.commit()
        return jsonify({'success': True, 'id': incident.id})
    
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return jsonify([{
        'id': i.id,
        'type': i.type,
        'description': i.description,
        'location': i.location,
        'latitude': i.latitude,
        'longitude': i.longitude,
        'status': i.status,
        'severity': i.severity,
        'created_at': i.created_at.isoformat(),
        'reporter': i.reporter.name if i.reporter else None
    } for i in incidents])

@app.route('/api/incidents/<int:id>/update', methods=['POST'])
@login_required
@admin_required
def api_update_incident(id):
    incident = Incident.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' in data:
        incident.status = data['status']
    if 'assigned_to' in data:
        incident.assigned_to = data['assigned_to']
    
    incident.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/dashboard_stats')
@login_required
def api_dashboard_stats():
    stats = {
        'total_incidents': Incident.query.count(),
        'active_incidents': Incident.query.filter(Incident.status.in_(['open', 'acknowledged', 'assigned'])).count(),
        'safe_checkins': Checkin.query.filter_by(status='safe').count(),
        'stuck_checkins': Checkin.query.filter_by(status='stuck').count(),
        'total_drills': Drill.query.count(),
        'emergency_contacts': EmergencyContact.query.filter_by(is_active=True).count()
    }
    return jsonify(stats)

# Student Management Routes
@app.route('/students')
@login_required
def students():
    """Student management page"""
    students = Student.query.order_by(Student.name).all()
    
    # Calculate some statistics
    active_students = Student.query.filter_by(status='active').count()
    pending_checkins = Student.query.filter(Student.last_checkin.is_(None)).count()
    
    # Calculate average drill participation
    if students:
        total_participation = sum(s.drill_participation for s in students)
        drill_participation = f"{total_participation // len(students)}%"
    else:
        drill_participation = "0%"
    
    return render_template('students_new.html', 
                         students=students,
                         active_students=active_students,
                         pending_checkins=pending_checkins,
                         drill_participation=drill_participation)

@app.route('/add_student', methods=['POST'])
@login_required
@admin_required
def add_student():
    """Add new student"""
    try:
        student = Student(
            student_id=request.form['student_id'],
            name=request.form['name'],
            class_name=request.form['class'],
            email=request.form.get('email', ''),
            emergency_contact_name=request.form['emergency_contact_name'],
            emergency_contact_phone=request.form['emergency_contact_phone'],
            medical_conditions=request.form.get('medical_conditions', ''),
            status='active'
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash('Student added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding student: {str(e)}', 'error')
        
    return redirect(url_for('students'))

@app.route('/api/students/<int:student_id>', methods=['GET'])
@login_required
def api_get_student(student_id):
    """Get student details"""
    student = Student.query.get_or_404(student_id)
    
    try:
        student_data = {
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'email': student.email,
            'class': student.class_name,
            'emergency_contact_name': student.emergency_contact_name,
            'emergency_contact_phone': student.emergency_contact_phone,
            'medical_conditions': student.medical_conditions,
            'drill_participation': student.drill_participation,
            'last_checkin': student.last_checkin.isoformat() if student.last_checkin else None,
            'status': student.status,
            'created_at': student.created_at.isoformat(),
            'updated_at': student.updated_at.isoformat()
        }
        
        return jsonify({'success': True, 'student': student_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/students/<int:student_id>/update', methods=['POST'])
@login_required
@admin_required
def api_update_student(student_id):
    """Update student information"""
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            student.name = data['name']
        if 'class' in data:
            student.class_name = data['class']
        if 'email' in data:
            student.email = data['email']
        if 'emergency_contact_name' in data:
            student.emergency_contact_name = data['emergency_contact_name']
        if 'emergency_contact_phone' in data:
            student.emergency_contact_phone = data['emergency_contact_phone']
        if 'medical_conditions' in data:
            student.medical_conditions = data['medical_conditions']
        if 'status' in data:
            student.status = data['status']
            
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/students/<int:student_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def api_delete_student(student_id):
    """Delete student"""
    student = Student.query.get_or_404(student_id)
    
    try:
        # Delete related drill participations
        StudentDrillParticipation.query.filter_by(student_id=student_id).delete()
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/students/<int:student_id>/checkin', methods=['POST'])
@login_required
def api_student_checkin(student_id):
    """Record student check-in"""
    student = Student.query.get_or_404(student_id)
    
    try:
        student.last_checkin = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'checkin_time': student.last_checkin.isoformat()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/drill/<int:drill_id>/student_participation', methods=['POST'])
@login_required
@admin_required
def api_record_drill_participation(drill_id):
    """Record student participation in drill"""
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    
    try:
        for student_id in student_ids:
            # Check if participation already recorded
            existing = StudentDrillParticipation.query.filter_by(
                student_id=student_id, 
                drill_id=drill_id
            ).first()
            
            if not existing:
                participation = StudentDrillParticipation(
                    student_id=student_id,
                    drill_id=drill_id,
                    participated=True,
                    score=data.get('score', 100)
                )
                db.session.add(participation)
                
                # Update student's participation percentage
                student = Student.query.get(student_id)
                if student:
                    total_drills = Drill.query.count()
                    participated_drills = StudentDrillParticipation.query.filter_by(
                        student_id=student_id, 
                        participated=True
                    ).count()
                    
                    if total_drills > 0:
                        student.drill_participation = min(100, int((participated_drills / total_drills) * 100))
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/drill/<int:drill_id>/save_participation', methods=['POST'])
@login_required
@admin_required
def api_save_drill_participation(drill_id):
    """Save drill participation data"""
    data = request.get_json()
    participation_data = data.get('participation_data', {})
    
    try:
        for student_id_str, participation in participation_data.items():
            student_id = int(student_id_str)
            
            # Check if participation already recorded
            existing = StudentDrillParticipation.query.filter_by(
                student_id=student_id, 
                drill_id=drill_id
            ).first()
            
            if existing:
                # Update existing record
                existing.participated = participation.get('participated', False)
                existing.score = float(participation.get('score', 0)) if participation.get('score') else None
                existing.feedback = participation.get('notes', '')
            else:
                # Create new record
                new_participation = StudentDrillParticipation(
                    student_id=student_id,
                    drill_id=drill_id,
                    participated=participation.get('participated', False),
                    score=float(participation.get('score', 0)) if participation.get('score') else None,
                    feedback=participation.get('notes', '')
                )
                db.session.add(new_participation)
            
            # Update student's overall participation percentage
            student = Student.query.get(student_id)
            if student:
                total_drills = Drill.query.count()
                participated_drills = StudentDrillParticipation.query.filter_by(
                    student_id=student_id, 
                    participated=True
                ).count()
                
                if total_drills > 0:
                    student.drill_participation = min(100, int((participated_drills / total_drills) * 100))
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/drill/<int:drill_id>/participation')
@login_required
def api_get_drill_participation(drill_id):
    """Get existing drill participation data"""
    participations = StudentDrillParticipation.query.filter_by(drill_id=drill_id).all()
    
    participation_data = {}
    for p in participations:
        participation_data[p.student_id] = {
            'participated': p.participated,
            'score': p.score or '',
            'notes': p.feedback or ''
        }
    
    return jsonify(participation_data)

@app.route('/api/students')
@login_required
def api_get_students():
    """Get all students data"""
    students = Student.query.order_by(Student.name).all()
    
    return jsonify([{
        'id': s.id,
        'student_id': s.student_id,
        'name': s.name,
        'email': s.email or '',
        'class': s.class_name,
        'emergency_contact_name': s.emergency_contact_name,
        'emergency_contact_phone': s.emergency_contact_phone,
        'medical_conditions': s.medical_conditions or '',
        'drill_participation': s.drill_participation,
        'last_checkin': s.last_checkin.isoformat() if s.last_checkin else None,
        'status': s.status,
        'created_at': s.created_at.isoformat()
    } for s in students])

@app.route('/drill_participation')
@login_required
def drill_participation():
    """Drill participation tracking page"""
    drills = Drill.query.order_by(Drill.created_at.desc()).all()
    return render_template('drill_participation.html', drills=drills)

# Initialize database
def init_db():
    with app.app_context():
        # For development, drop and recreate all tables to ensure clean schema
        print("Initializing database...")
        db.drop_all()
        db.create_all()
        print("✅ Database tables created")
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@emergency.gov').first()
        if not admin:
            admin = User(
                name='System Administrator',
                email='admin@emergency.gov',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print("✅ Admin user created")
        
        # Create some sample data for testing
        create_sample_data()
        
        db.session.commit()
        print("✅ Database initialization complete")

def create_sample_data():
    """Create some sample drills for testing"""
    try:
        # Check if we already have drills
        if Drill.query.count() == 0:
            sample_drills = [
                Drill(
                    title='Fire Evacuation Drill',
                    description='Practice fire evacuation procedures',
                    drill_type='fire',
                    location='Building A - Ground Floor',
                    scheduled_date=datetime.now() + timedelta(days=2),
                    total_expected=50,
                    conducted_by=1
                ),
                Drill(
                    title='Earthquake Safety Drill',
                    description='Learn earthquake response procedures',
                    drill_type='earthquake', 
                    location='Auditorium',
                    scheduled_date=datetime.now() + timedelta(days=5),
                    total_expected=75,
                    conducted_by=1
                ),
                Drill(
                    title='Flood Response Training',
                    description='Flood emergency response training',
                    drill_type='flood',
                    location='Community Hall',
                    scheduled_date=datetime.now() + timedelta(days=8),
                    total_expected=60,
                    conducted_by=1
                )
            ]
            
            for drill in sample_drills:
                db.session.add(drill)
            
            print("✅ Sample drills created")
    except Exception as e:
        print(f"Error creating sample data: {e}")

def migrate_database():
    """Migrate database to add new columns if they don't exist - Not needed in clean initialization"""
    pass

@app.route('/settings')
@login_required
def settings():
    """Admin settings page"""
    return render_template('settings.html')

# Error handlers
# Public API endpoints for student access (no login required)
@app.route('/api/public/drills', methods=['GET'])
def public_drills():
    """Public endpoint for students to access drill data"""
    try:
        # Get all active drills
        drills = Drill.query.order_by(Drill.created_at.desc()).all()
        
        drill_list = []
        for drill in drills:
            # Use scheduled_date if available, otherwise calculate from creation date
            try:
                if hasattr(drill, 'scheduled_date') and drill.scheduled_date:
                    drill_date = drill.scheduled_date
                else:
                    drill_date = drill.created_at + timedelta(days=1)  # Example: drill is next day after creation
            except:
                drill_date = drill.created_at + timedelta(days=1)
            
            # Get location safely
            try:
                location = drill.location if hasattr(drill, 'location') and drill.location else 'IGDTUW Campus'
            except:
                location = 'IGDTUW Campus'
            
            drill_data = {
                'id': drill.id,
                'title': drill.title,
                'description': drill.description,
                'drill_type': drill.drill_type,
                'location': location,
                'total_expected': drill.total_expected,
                'participation_count': drill.participation_count,
                'score': drill.score,
                'file_url': drill.file_url,
                'created_at': drill.created_at.isoformat(),
                'scheduled_date': drill_date.isoformat(),
                'status': 'scheduled',  # Default status for new drills
                'conductor_name': drill.conductor.name if drill.conductor else 'Administrator'
            }
            drill_list.append(drill_data)
        
        return jsonify({
            'success': True,
            'drills': drill_list,
            'total_count': len(drill_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/public/drills/<int:drill_id>/participate', methods=['POST'])
def public_drill_participate(drill_id):
    """Public endpoint for students to mark participation in a drill"""
    try:
        data = request.get_json()
        student_name = data.get('student_name', 'Anonymous Student')
        student_id = data.get('student_id', 'unknown')
        
        drill = Drill.query.get_or_404(drill_id)
        
        # Increment participation count
        drill.participation_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Participation recorded for {student_name}',
            'drill_id': drill_id,
            'new_participation_count': drill.participation_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

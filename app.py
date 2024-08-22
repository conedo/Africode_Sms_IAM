from flask import Flask, render_template, request, url_for, redirect, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, roles_required, hash_password
from flask_security.forms import RegisterForm
from flask_migrate import Migrate
from flask_mailman import Mail
import config

app = Flask(__name__)
Bootstrap5(app)
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    webauthn = db.relationship('WebAuth', backref='user', uselist=False)

class WebAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    teacher = db.relationship('User', backref='course_taught')  # Fixed: Changed 'user' to 'User'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref='enrollment')
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student = db.relationship('User', backref='enrollments')
    grade = db.Column(db.Float, nullable=True)  # Fixed: Changed db.Float(225) to db.Float

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
mail = Mail(app)

@app.route('/')
@login_required
def index():
    courses_count = Course.query.count()
    students_count = User.query.join(User.roles).filter(Role.name == 'Student').count()
    teachers_count = User.query.join(User.roles).filter(Role.name == 'Teacher').count()
    
    enrollment = None
    if current_user.has_role('Student'):
        enrollment = Enrollment.query.filter_by(student_id=current_user.id).first()
    return render_template('index.html',courses_count = courses_count, students_count = students_count, teachers_count = teachers_count,enrollment = enrollment)

@app.route('/courses')
@login_required
def courses():
    if current_user.has_role('Admin') or current_user.has_role('Teacher'):
        courses = Course.query.all()
    else:
        courses = Course.query.all()
        # changed something

    return render_template('courses.html', courses=courses)  # Fixed: Moved return outside the else block


@app.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    
    return render_template('course_details.html', course=course)  


@app.route('/create_course', methods=['GET', 'POST'])
@roles_required('Admin')
def create_course():
    if request.method == 'POST':
        name = request.form.get('name')
        teacher_id = request.form.get('teacher_id')
        course = Course(name=name, teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!')
        return redirect(url_for('courses'))
    teachers = User.query.join(roles_users).join(User.roles).filter(Role.name == 'Teacher').all()  # Fixed: Corrected query for filtering teachers
    return render_template('create_course.html', teachers=teachers)

@app.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
@roles_required('Student')
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    if Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first():
        flash('You are already enrolled in this course!')
    else:
        enrollment = Enrollment(course_id=course_id, student_id=current_user.id)
        db.session.add(enrollment)
        db.session.commit()
        flash('You have been enrolled in this course!')
    return redirect(url_for('course_details', course_id= course_id))  # Fixed: Moved return outside the else block

@app.route('/grade/<int:enrollment_id>', methods=['GET', 'POST'])
@roles_required('Teacher')
def grade(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.course.teacher_id != current_user.id:
        flash('You are not a teacher of this course.')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        grade = request.form.get('grade')
        enrollment.grade = float(grade)
        db.session.commit()
        flash('Grade updated successfully!')
        return redirect(url_for('course_details', course_id=enrollment.course_id))

    # This renders the grade.html template when accessed via a GET request
    # return render_template('grade.html', enrollment=enrollment)

@app.route('/view_grades')
@roles_required('Student')  # Only students should access this page
@login_required
def view_grades():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('view_grades.html', enrollments=enrollments)

@app.route('/manage_students')
@roles_required('Teacher')
def manage_students():
    # Fetch the courses taught by the current teacher
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('manage_students.html', courses=courses)

@app.route('/grade_course/<int:course_id>', methods=['GET', 'POST'])
@roles_required('Teacher')
def grade_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if the current user is the teacher of this course
    if course.teacher_id != current_user.id:
        flash('You are not the teacher of this course')
        return redirect(url_for('manage_students'))
    
    # Fetch all enrollments for this course
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    return render_template('grade_course.html', course=course, enrollments=enrollments)

@app.route('/manage_courses')
@roles_required('Teacher')
@login_required
def manage_courses():
    # Fetch the courses taught by the current teacher
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('manage_courses.html', courses=courses)


@app.route('/register_user', methods=['GET', 'POST'])
@roles_required('Admin')
def register_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role_name = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
        else:
            role = user_datastore.find_role(role_name)
            hashed_password = hash_password(password)
            user_datastore.create_user(email=email, password=hashed_password, roles=[role])
            db.session.commit()
            flash(f'{role_name} registered successfully!')
        return redirect(url_for('index'))

    return render_template('register_user.html')




@app.route('/delete_course/<int:course_id>', methods=['POST'])
@roles_required('Teacher')
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Ensure the current user is the teacher of the course
    if course.teacher_id != current_user.id:
        flash('You do not have permission to delete this course.', 'danger')
        return redirect(url_for('manage_courses'))

    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('manage_courses'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # create roles
        user_datastore.find_or_create_role(name='Admin', description='Administrator')
        user_datastore.find_or_create_role(name='Teacher', description='Teacher')
        user_datastore.find_or_create_role(name='Student', description='Student')

        # create users
        if not user_datastore.find_user(email='dollychepkorir@gmail.com'):
            hashed_password = hash_password('password')
            user_datastore.create_user(email='dollychepkorir@gmail.com', password=hashed_password, roles=[user_datastore.find_role('Admin')])
            db.session.commit()

        if not user_datastore.find_user(email='chepkorirdolly4@gmail.com'):
            hashed_password = hash_password('password')
            user_datastore.create_user(email='chepkorirdolly4@gmail.com', password=hashed_password, roles=[user_datastore.find_role('Teacher')])
            db.session.commit()

        if not user_datastore.find_user(email='chelangatgladwel9@gmail.com'):
            hashed_password = hash_password('password')
            user_datastore.create_user(email='chelangatgladwel9@gmail.com', password=hashed_password, roles=[user_datastore.find_role('Student')])
            db.session.commit()


    app.run(port=8000 ,debug=True)

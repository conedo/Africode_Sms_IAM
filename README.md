# Flask-Security-Based School Management System (Sms)

This project is a learning management system (Sms) built using Flask, Flask-Security, and other Flask extensions. The system allows for user registration, role-based access control, course creation, enrollment, and grading.

## Installation

To set up the project, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/your-username/flask-security-lms.git
cd flask-security-lms
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a configuration file named `config.py` in the root directory of the project. Add the following code to set up the necessary configurations:

```python
import os

SECRET_KEY = os.urandom(32)
SQLALCHEMY_DATABASE_URI = 'sqlite:///lms.db'  # Use your preferred database URI
MAIL_SERVER = 'your_mail_server'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_mail_username'
MAIL_PASSWORD = 'your_mail_password'
```

5. Initialize the database and create roles:
```bash
python app.py
```

6. Run the application:
```bash
python app.py
```

Now you can access the Sms at http://localhost:5000.

## Features

- User registration with email confirmation
- Role-based access control (Admin, Teacher, Student)
- Course creation and management (Admin only)
- Student enrollment in courses
- Teacher grading of students' assignments
- Email notifications for course enrollment and grade updates

## Usage

- Admin users can create courses, register students, and manage roles.
- Teacher users can create courses, view enrolled students, and grade assignments.
- Student users can enroll in courses, view course details, and receive grade updates.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.


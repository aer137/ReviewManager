"""
    Patients API server
    to run: 
source .venv/bin/activate
export FLASK_APP=application.py
export FLASK_ENV=development
flask run

"""

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.orm import aliased

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'


db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    excel_sheet = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    wrote_review = db.Column(db.Boolean, nullable=False)
    name_on_google = db.Column(db.String, nullable=True)

    def __repr__(self):
        # overwrite repr[esent] method, for when we want to print the loan data
        return f"${self.name} - wrote review: {self.wrote_review}"

# set up endpoint
@app.route('/')
def index():
    return 'Hello!'


@app.route('/patients')
# get - plural
def get_patients():
    patients = Patient.query.all()
    output = []
    for patient in patients:
        patient_data = {
            'name' : patient.name,
            'excel_sheet' : patient.excel_sheet,
            'phone' : patient.phone,
            'email' : patient.email,
            'wrote_review' : patient.wrote_review,
            'name_on_google' : patient.name_on_google,
        }
        output.append(patient_data)
    return {"patients": output}

@app.route('/patients/<name>')
# get - singular
def get_patient(name):
    patient = Patient.query.filter_by(name=name).first_or_404()
    return {
            'name' : patient.name,
            'excel_sheet' : patient.excel_sheet,
            'phone' : patient.phone,
            'email' : patient.email,
            'wrote_review' : patient.wrote_review,
            'name_on_google' : patient.name_on_google,
        }


@app.route('/patients', methods=['POST'])
# post
def add_patient():
    patient = Patient(
        name=request.json['name'],
        excel_sheet=request.json['excel_sheet'],
        phone=request.json['phone'],
        email=request.json['email'],
        wrote_review=request.json['wrote_review'],
        name_on_google=request.json['name_on_google']
    )
    patient_exists = Patient.query.filter_by(name=patient.name)
    if patient_exists != None:
        db.session.add(patient)
        db.session.commit()
        return {'name' : patient.name}
    else:
        return {'patient' : 'already in records'}


@app.route('/patients/<name>', methods=['PUT'])
# put
def modify_patient(name):
    patient = Patient.query.filter_by(name=name).first_or_404()
    req = request.json
    keys = ["name", "excel_sheet", "phone", "email", "wrote_review", "name_on_google"]
    for key in keys:
        if key in req:
            setattr(patient, key, req[key])

    db.session.commit()
    return {'name' : patient.name}

@app.route('/patients/<name>', methods=['DELETE'])
# delete
def delete_patient(name):
    patient = Patient.query.filter_by(name=name).first_or_404()
    if patient is None:
        return {"error" : "not found"}
    db.session.delete(patient)
    db.session.commit()
    return {"message" : "yeet deleted"}


@app.route('/requestAgain')
# get patients who haven't reviewed
def request_again():
    patients = Patient.query.filter_by(wrote_review=0)
    output = []
    for patient in patients:
        patient_data = {
            'name' : patient.name,
            'excel_sheet' : patient.excel_sheet,
            'phone' : patient.phone,
            'email' : patient.email,
            'wrote_review' : patient.wrote_review,
            'name_on_google' : patient.name_on_google,
        }
        output.append(patient_data)
    return {"patients": output}

# app.run(host='0.0.0.0', port=80)

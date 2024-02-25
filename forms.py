from db_data import *
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, equal_to


class vraagForm(FlaskForm):
    db_connection = connect_to_database("testcorrect_vragen.db")
    leerdoelen = get_db_data(
        db_connection, f"SELECT * FROM leerdoelen").fetchall()

    leerdoel = SelectField(u'Leerdoel', validators=[DataRequired()], choices=[(leerdoel['id'], f"{leerdoel['id']} - {leerdoel['leerdoel']}") for leerdoel in leerdoelen])
    vraag = TextAreaField(validators=[DataRequired(), Length(min=1, max=500)])
    opslaan = SubmitField("Wijzigingen opslaan")


class RegistratieForm(FlaskForm):
    gebruikersnaam = StringField('Gebruikersnaam', validators=[
                                 DataRequired(), Length(min=2, max=20)])
    wachtwoord = PasswordField('Wachtwoord', validators=[DataRequired()])
    bevestig_wachtwoord = PasswordField('Bevestig wachtwoord', validators=[
                                        DataRequired(), equal_to('wachtwoord')])
    indienen = SubmitField('Registreer')


class LoginForm(FlaskForm):
    gebruikersnaam = StringField("Gebruikersnaam", validators=[
                                 DataRequired(), Length(min=2, max=20)])
    wachtwoord = PasswordField("Wachtwoord", validators=[DataRequired()])
    herinner = BooleanField("Herinner mij")
    indienen = SubmitField("Log in")

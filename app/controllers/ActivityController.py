from flask import render_template
from app import app

@app.route('/activity')
def activity():
    return render_template('Activity/Activity.html')
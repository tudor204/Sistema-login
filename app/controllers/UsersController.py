from flask import render_template, redirect, url_for, flash
from flask_login import logout_user, login_required
from app import app


@app.route('/profile')
@login_required
def profile():
    return render_template('Users/profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))



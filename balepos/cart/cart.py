from flask import Blueprint,render_template
from flask import current_app as app
from datetime import datetime
from flask import session

cart_bp=Blueprint('cart_bp',__name__,static_folder='static',template_folder='templates')

@cart_bp.route('/<table>/cart',methods=['GET'])

def cart(table):
    orderlist=session['theOrder']
    print(orderlist)

    return render_template('cart.html',orders=orderlist)

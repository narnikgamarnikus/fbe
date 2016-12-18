# coding: utf-8
from flask import render_template, Blueprint, request
import stripe
from config import load_config
from ..models import db, Operation, User

config = load_config()
secret_key = config.SECRET_KEY
default_charge_amount = config.DEFAULT_CHARGE_AMOUNT

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """Index page."""
    db.create_all()
    return render_template('site/index/index.html',
    	key=secret_key,
    	amount_usd=get_amount_usd()
    	)

	
def get_stripe_customer(customer_email):
	print('Customer email is : ' + str(customer_email)) 
	customer_info = User.query.order_by('email' == customer_email).first()
	if(customer_info == None):
		return False, customer_info
		print('Customer info is : ' + str(customer_info))
	else:
		return True, customer_info
		print('Customer info is : ' + str(customer_info))

	

#-----------------------------------
def save_stripe_customer(customer_email, customer_id):

	# If already have a customer by that email, delete old entry
	reply, entry = get_stripe_customer(customer_email)
	if(reply):
		'''
		user = User.query.filter_by(email = customer_email)
		db.session.remove(user)
		db.session.commit()
		'''
		print('Preply is : ' + reply)
	else:
		user = User(name = customer_email.split('@')[0], email = customer_email)
		db.session.add(user)
		db.session.commit()
		save_stripe_operation(customer_id)



def save_stripe_operation(customer_id):
	operation = Operation(costomer_id)
	db.sessoin.add(operation)
	db.session.commit()


#-----------------------------------
def stripe_charge(customer_id,
			charge_amount=default_charge_amount,
			charge_descripton='fbe'):

	try:		
		charge = stripe.Charge.create(
			customer=customer_id,
			amount=charge_amount,
			currency='usd',
			description=charge_descripton 
			)

	except stripe.CardError as e:
		
		# The card has been declined (or other error)
		return False, e 

	return True, "successfully charged"

@bp.route('/charge', methods=['POST'])
def charge():

	customer_email = request.form['email']

	# Check if already have this customer
	customer_valid, customer_info = get_stripe_customer(customer_email)

	if(customer_valid):
		customer_id = customer_info['user.id']
		print(customer_id)
	else:
		print(request.form['stripeToken'])
		print('asd')

		customer = stripe.Customer.create(
					email=customer_email,
					card=request.form['stripeToken'],
					)		

		customer_id = customer.id
		# save the customer ID in DB for later use
		save_stripe_customer(customer_email, customer_id)
		return True
	# charge the customer (new or already present in DB)
	charge_valid, charge_msg = stripe_charge(customer_id)
	
	return render_template('/charge/charge.html',
		amount_usd=get_amount_usd(), 
		customer_email=customer_email,
		charge_valid=charge_valid,
		charge_msg=charge_msg)


@bp.route('/recurring', methods=['POST'])
def recurring():

	customer_email = request.form['email']

	# Get customer_id from Mongo
	customer_valid, customer_info = get_stripe_customer(customer_email)

	if(customer_valid):
		customer_id = customer_info['customer_id']
		
		# Charge the customer (new or already present in DB)
		charge_valid, charge_msg = stripe_charge(customer_id)

	else:
		charge_valid = False
		charge_msg = "recurring customer doesn't exist"
		print(charge_msg)

	return render_template('/charge/charge.html', 
		amount_usd=get_amount_usd(), 
		customer_email=customer_email,
		charge_valid=charge_valid,
		charge_msg=charge_msg)


def get_amount_usd(amount=default_charge_amount):
	return float(amount) / 100


@bp.route('/about')
def about():
    """About page."""
    return render_template('site/about/about.html')

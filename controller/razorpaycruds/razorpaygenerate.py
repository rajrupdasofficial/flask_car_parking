import os
import random
import psycopg2
import razorpay

# Set up Razorpay client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZOR_PAY_KEY"), os.getenv("RAZOR_PAY_SECRET")))

def create_payment(payment_details):
    # Destructure required fields from payment_details
    customer_name =payment_details['firstname']
    customer_email = payment_details['email']
    # customer_address = payment_details['address']
    price = payment_details['price']

    print("Razorpay captured price", price)

    # Create an order in Razorpay
    order_data = {
        "amount": price * 100,  # Amount in paise (multiply by 100 to convert to paise)
        "currency": "INR",
        "receipt": f"receipt_{random.randint(1000, 9999)}",  # Unique receipt ID
        "notes": {
            "address": 'Amount for wallet recharge'  # Use customerAddress for address
        }
    }

    try:
        order = razorpay_client.order.create(data=order_data)

        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()

        # Insert payment details into the database (example table structure)
        insert_query = """
            INSERT INTO payments (order_id, customer_name, customer_email, amount, currency)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (order['id'], customer_name, customer_email, order['amount'], order['currency']))
        conn.commit()

        # Return order details to the caller
        return {
            "id": order['id'],
            "amount": order['amount'],
            "currency": order['currency'],
            "key_id": os.getenv("RAZOR_PAY_KEY"),
            "name": 'Transmogrify Global Pvt. Ltd',
            "description": 'Payment for Total Revenue',
            "image": 'https://cdn.statically.io/img/transmogriffy.com/wp-content/uploads/2022/03/TWLD5456.jpg?w=1280&quality=100&f=auto',
            "prefill": {
                "name": customer_name,
                "email": customer_email,
                "contact": '',  # Assuming contact is not provided; you may want to add this if available
            },
            "theme": {
                "color": "#F37254"
            }
        }
    except Exception as e:
        print('Error creating payment:', e)
        raise Exception(f"Payment creation failed - {str(e)}")  # More informative error message
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
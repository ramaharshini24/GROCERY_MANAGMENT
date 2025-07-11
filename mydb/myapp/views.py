from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.contrib import messages
from django.db import OperationalError, transaction

def index(request):
    return render(request, 'myapp/index.html')


def customer_login(request):
    error_message = None


    if request.method == "POST":
        userid = request.POST.get('userid')

        if userid and len(userid) > 0:
            # check if the userid exists in the customers table
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM customers WHERE customer_id = %s;", [userid])
                row = cursor.fetchall()
                customer_exists = len(row) > 0

            if customer_exists:
                request.session['user_id'] = userid
                # Redirect to the customer products page if userid is found
                return redirect('customer_product')
            else:
                # Set the error message to display in the template
                error_message = "Invalid User ID. Please try again."
        else:
            # Set the error message for empty user ID field
            error_message = "User ID cannot be empty."

    # Render the login page with error_message and new_cust_id if any
    return render(request, 'myapp/customer_login.html', {
        'error_message': error_message,
        #'new_cust_id': new_cust_id  # Pass the new customer ID to the template
    })
                #return render(request, 'myapp/customer_login.html')




def customer_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        city = request.POST.get('city')
        number = request.POST.get('number')
        street = request.POST.get('street')
        house = request.POST.get('house')

        # Call the stored procedure to insert a new customer
        with connection.cursor() as cursor:
            cursor.callproc('new_cust', [name, number, street, house, city])
            new_cust_id = cursor.fetchone()[0]  # Fetch the new customer ID

        # Store the new customer ID in the session to display it on the login page
        request.session['new_cust_id'] = new_cust_id

        # Redirect to the customer login page
        return HttpResponse(f"""
                    <html>
                    <head>
                        <script type="text/javascript">
                            // Redirect to login after 5 seconds
                            setTimeout(function() {{
                                window.location.href = '/customer_login';  
                            }}, 5000);
                        </script>
                    </head>
                    <body>
                        <h2>Thank you for signing up!</h2>
                        <p>Your customer ID is: {new_cust_id}</p>  <!-- Display the new customer ID -->
                        <p>You will be redirected to the login page shortly...</p>
                    </body>
                    </html>
                """)

    return render(request, 'myapp/customer_signup.html')

def customer_product(request):

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('customer_login')

    # Fetch customer product details
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.product_id, p.product_name, p.stock, COALESCE(AVG(r.rating), 0) AS avg_rating
            FROM products p
            LEFT JOIN product_rating r ON p.product_id = r.product_id
            GROUP BY p.product_id, p.product_name, p.stock;
        """)
        products_with_ratings = cursor.fetchall()

        # Convert the result to a list of dictionaries to pass to the template
    products_list = []
    for product in products_with_ratings:
            products_list.append({
                'product_id': product[0],
                'product_name': product[1],
                'stock': product[2],
                'rating': product[3]  # This will either be the average rating or 0 if no ratings exist
            })

    # Pass the product list to the template
    return render(request, 'myapp/customer_product.html', {'products': products_list})

    #return render(request, 'myapp/customer_product.html')


def place_order(request, product_id):
    if request.method == 'POST':
        action_type = request.POST.get('action_type')  # Identify which form is being submitted
        customer_id = request.session.get('user_id')  # Assuming customer_id is the logged-in user's ID

        try:
            if action_type == 'order':
                # Handling product order
                quantity_ordered = int(request.POST.get('quantity', 1))

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.callproc('place_order', [product_id, customer_id, quantity_ordered])
                return render(request, 'myapp/customer_product.html', {
                    'success_message': 'Order Placed.'
                })
                #return redirect('customer_product')

            elif action_type == 'rating':
                # Handling product rating
                rating = request.POST.get('rating')

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO product_rating (product_id, customer_id, rating) VALUES (%s, %s, %s)",
                                   [product_id, customer_id, rating])



        except OperationalError as e:
            error_message = str(e)
            if 'Not enough stock available for this product' in error_message:
                return render(request, 'myapp/customer_product.html', {
                    'error_message': 'Not enough stock available for this product.'
                })
            elif 'Cannot give a product rating without placing an order for the product' in error_message:
                return render(request, 'myapp/customer_product.html', {
                    'error_message': 'You must place an order for this product before giving a rating.'
                })
            else:
                return render(request, 'myapp/customer_product.html', {
                    'error_message': f'An error occurred: {error_message}'
                })

    return render(request, 'myapp/customer_product.html')


def add_cust_phone_number(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        phone_number = request.POST.get('phone_number')

        # Add the new_ph_no
        with connection.cursor() as cursor:
            cursor.execute('insert into customer_ph_no values(%s,%s)', [user_id,phone_number])

        # Redirect after adding the phone number
        return redirect('customer_product')

    # If the request is GET, just render the form
    return render(request, 'myapp/add_cust_phone_number.html')

def add_address(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        house_no = request.POST.get('house')
        street = request.POST.get('street')
        city = request.POST.get('city')

        # Add the new_address
        with connection.cursor() as cursor:
            cursor.execute('insert into customer_addresses values(%s,%s,%s,%s);', [user_id,house_no,street,city])

        # Redirect
        return redirect('customer_product')

    # If the request is GET, just render the form
    return render(request, 'myapp/add_address.html')

def my_details(request):
    # Assuming the user is authenticated
    user_id = request.session.get('user_id')

    # Fetch customer details
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", [user_id])
        customer = cursor.fetchone()  # Fetch one row

    # Fetch customer phone numbers
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customer_ph_no WHERE customer_id = %s", [user_id])
        phone_numbers = cursor.fetchall()  # Fetch all rows

    # Fetch customer addresses
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customer_addresses WHERE customer_id = %s", [user_id])
        addresses = cursor.fetchall()  # Fetch all rows

    # Prepare the context with customer data
    context = {
        'customer': customer,
        'phone_numbers': phone_numbers,
        'addresses': addresses,
    }

    # Render the 'my_details.html' template with the customer details
    return render(request, 'myapp/my_details.html', context)


def seller_login(request):
    error_message = None

    if request.method == "POST":
        userid = request.POST.get('userid')

        if userid and len(userid) > 0:
            # check if the userid exists in the customers table
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM sellers WHERE seller_id = %s;", [userid])
                row = cursor.fetchall()
                seller_exists = len(row) > 0

            if seller_exists:
                request.session['userid'] = userid
                # Redirect to the customer products page if userid is found
                return redirect('seller_home')
            else:
                # Set the error message to display in the template
                error_message = "Invalid User ID. Please try again."
        else:
            # Set the error message for empty user ID field
            error_message = "User ID cannot be empty."

    # Render the login page with error_message and new_cust_id if any
    return render(request, 'myapp/seller_login.html', {
        'error_message': error_message,
    })

def seller_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')

        number = request.POST.get('number')


        # Call the stored procedure to insert a new customer
        with connection.cursor() as cursor:
            cursor.callproc('new_seller', [name, number])
            new_seller_id = cursor.fetchone()[0]  # Fetch the new customer ID

        # Store the new seller ID in the session to display it on the login page
        request.session['new_seller_id'] = new_seller_id

        # Redirect to the customer login page
        return HttpResponse(f"""
                    <html>
                    <head>
                        <script type="text/javascript">
                            // Redirect to login after 5 seconds
                            setTimeout(function() {{
                                window.location.href = '/seller_login';  
                            }}, 5000);
                        </script>
                    </head>
                    <body>
                        <h2>Thank you for signing up!</h2>
                        <p>Your Seller ID is: {new_seller_id}</p>  <!-- Display the new customer ID -->
                        <p>You will be redirected to the login page shortly...</p>
                    </body>
                    </html>
                """)

    return render(request, 'myapp/seller_signup.html')

def seller_home(request):
    # Ensure user is logged in, otherwise redirect to login page
    seller_id = request.session.get('userid')  # Assuming the seller is logged in


    if not seller_id:  # If no seller ID is found in session, redirect to login
        return redirect('seller_login')

    # Fetch seller's products from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT product_id,product_name, stock FROM products WHERE seller_id = %s", [seller_id])
        products = cursor.fetchall()

    # Pass data to the template
    products_list = []
    for product in products:
        products_list.append({
            'product_id': product[0],
            'product_name': product[1],
            'stock': product[2],

        })

    # Pass the product list to the template
    return render(request, 'myapp/seller_home.html', {'products': products_list})



def add_product(request):
        if request.method == 'POST':
            product_name = request.POST['product_name']
            product_stock = request.POST['product_stock']
            seller_id = request.session.get('userid') # Get seller_id from session

            with connection.cursor() as cursor:
                cursor.callproc('new_product', [product_name, product_stock, seller_id])

            return redirect('seller_home')
        return render(request, 'myapp/add_product.html')

def add_seller_phone_number(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        seller_id = request.session.get('userid')  # Get seller_id from session

        # Ensure the seller_id exists in the session
        if not seller_id:
            return redirect('seller_login')  # Redirect to login if not logged in

        # Insert the phone number for the seller
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO seller_ph_no (seller_id, phone_number) VALUES (%s, %s);", [seller_id, phone_number])

        # Redirect to seller home after successfully adding the phone number
        return redirect('seller_home')

    return render(request, 'myapp/add_seller_phone_number.html')




def seller_details(request):

        seller_id = request.session.get('userid')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sellers WHERE seller_id = %s", [seller_id])
            seller = cursor.fetchone()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM seller_ph_no WHERE seller_id = %s", [seller_id])
            phone_numbers = cursor.fetchall()  # Fetch all rows
        phone_numbers_list = [phone[0] for phone in phone_numbers] if phone_numbers else []

        if seller:
            seller_details = {
                'seller_id': seller[0],
                'name': seller[1],
                'phone_number': phone_numbers_list,
            }

            return render(request, 'myapp/seller_details.html', {'seller_details': seller_details})
        else:
            return render(request, 'myapp/seller_home.html')


# View to choose delivery partner
def choose_delivery_partner(request):
    seller_id = request.session.get('userid')
    if not seller_id:
        return redirect('seller_login')

    if request.method == 'POST':
        delivery_partner_id = request.POST.get('delivery_partner_id')
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO delivery (seller_id, delivery_partner_id) VALUES (%s, %s) ;",
                [seller_id, delivery_partner_id]
            )
        return redirect('seller_home')

    # Fetch available delivery partners
    with connection.cursor() as cursor:
        cursor.execute("SELECT delivery_partner_id, delivery_partner_name FROM delivery_partners")
        delivery_partners = cursor.fetchall()

    delivery_partners_list = [{'delivery_partner_id': p[0], 'name': p[1]} for p in delivery_partners]

    return render(request, 'myapp/choose_delivery_partner.html', {'delivery_partners': delivery_partners_list})

def update_stock(request):
    seller_id = request.session.get('userid')  # Ensure seller is logged in
    if not seller_id:
        return redirect('seller_login')

    if request.method == 'POST':
        # Loop through the posted data and update the stock for each product
        for key, value in request.POST.items():
            if key.startswith('stock_'):
                product_id = key.split('_')[1]  # Extract the product ID from the form name (e.g., stock_1)
                stock_value = value

                # Update the stock for the corresponding product in the database
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE products SET stock = %s WHERE product_id = %s AND seller_id = %s",
                                   [stock_value, product_id, seller_id])

        return redirect('seller_home')
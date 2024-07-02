### CONTENTS

1. Project Overview
2. Data Models
3. User Flow 
    - 3.1 Browsing Products
    - 3.2 Adding to Cart
    - 3.3 Checkout Process
    - 3.4 Order Confirmation
4. Admin Flow
    - 4.1 Viewing Orders
    - 4.2 Updating Order Status
    - 4.3 Managing Products
5. Key Data Flows
    - 5.1 Cart Management
    - 5.2 Order Creation
    - 5.3 Payment Processing
    - 5.4 Order Status Updates


### 1. Project Overview

a) Name and purpose

- The name of this project is Tech Accessories
- It is an online store for selling mainly computer and phone accessories
- 

b) Key Features

- Product browsing and search
- Shopping cart functionality
- User account management (if implemented)
- Secure checkout process
- Order management for administrators
- 

c) Technology Stack

- Backend: Python with Flask framework
- Database: SQLite
- Frontend: HTML, CSS (Bootstrap), JavaScript
- Payment Processing: Stripe API
- 

Admin Dashboard:

- Order management interface on front end
- Protected by Admin Password

Database:

- Stores product information, orders, and user data

External Integrations:

- Stripe for payment processing

e) Basic Architecture

- The application follows a Model-View-Controller (MVC) architecture. Flask handles routing and controller logic, SQLAlchemy is used for database models, and Jinja2 templates render the views.

f) Security and Compliance Highlights

- Secure handling of payment information via Stripe
- Admin authentication for accessing the dashboard

g) Future Enhancements

- Implement a sign in dialogue after customer purchase. The customer dashboard will have product tracking and ability to leave product reviews.
- More product categories with links on the nav bar.
- Home page - hero section and marketing features.
- Product pages with star ratings from reviews
- Complete footer links: Help centre, contact, FAQs, terms of service, privacy policy, cookie policy.
- Site Chatbot based on docs and footer links.
- Order management system with automatic tracking and more intuitive fulfilment with supplier.
- Email confirmation



### 2. Data Models

Data models represent the structure of the data stored in our application's database. They define the attributes of each entity and the relationships between different entities. Our application uses SQLAlchemy as an ORM (Object-Relational Mapping) to interact with the database.”

1. Product Model
    - Represents items available for purchase in the store
    - Fields:
        - id (Integer, Primary Key): Unique identifier for the product
        - name (String, Not Null): Name of the product
        - description (Text): Detailed description of the product
        - price (Float, Not Null): Price of the product
        - image_url (String): URL to the product's image
        - supplier_url (String): URL to the supplier's page for this product
    - Relationships:
        - order_items: One-to-Many relationship with OrderItem model
2. Order Model
    - Represents a customer's order
    - Fields:
        - id (Integer, Primary Key): Unique identifier for the order
        - stripe_session_id (String): ID of the Stripe session for this order
        - customer_name (String, Not Null): Name of the customer
        - customer_email (String, Not Null): Email of the customer
        - total_amount (Float, Not Null): Total amount of the order
        - status (String, Not Null): Current status of the order (e.g., 'paid', 'processing', 'shipped', 'delivered')
        - created_at (DateTime, Not Null): Timestamp of when the order was created
    - Relationships:
        - items: One-to-Many relationship with OrderItem model
        - shipping_details: One-to-One relationship with ShippingDetails model
3. OrderItem Model
    - Represents individual items within an order
    - Fields:
        - id (Integer, Primary Key): Unique identifier for the order item
        - order_id (Integer, Foreign Key): ID of the associated order
        - product_id (Integer, Foreign Key): ID of the associated product
        - quantity (Integer, Not Null): Quantity of the product ordered
        - price_per_unit (Float, Not Null): Price per unit at the time of order
    - Relationships:
        - order: Many-to-One relationship with Order model
        - product: Many-to-One relationship with Product model
4. ShippingDetails Model
    - Represents shipping information for an order
    - Fields:
        - id (Integer, Primary Key): Unique identifier for the shipping details
        - order_id (Integer, Foreign Key): ID of the associated order
        - address_line1 (String, Not Null): First line of the shipping address
        - address_line2 (String): Second line of the shipping address (optional)
        - city (String, Not Null): City for shipping
        - state (String, Not Null): State or region for shipping
        - country (String, Not Null): Country for shipping
        - postal_code (String, Not Null): Postal or ZIP code for shipping
    - Relationships:
        - order: One-to-One relationship with Order model
5. CartItem Model
    - Represents items in a user's shopping cart
    - Fields:
        - id (Integer, Primary Key): Unique identifier for the cart item
        - cart_id (String, Not Null): Identifier for the cart (typically stored in session)
        - product_id (Integer, Foreign Key): ID of the associated product
        - quantity (Integer, Not Null): Quantity of the product in the cart
    - Relationships:
        - product: Many-to-One relationship with Product model
        
    

    
    ### 3 User Flow
    
    3.1 Browsing Products
    
    a) Landing Page
    
    - User arrives at the homepage
    - Relevant route: **`@app.route('/')`**
    - Key components displayed:
        - Featured products
        - Navigation menu
    
    b) Product Details
    
    - User views detailed information about a specific product
    - Relevant route: **`@app.route('/product/<int:product_id>')`**
    - Data displayed: Product name, description, price, image
    - Interaction: "Add to Cart" button
    
    3.2 Adding to Cart
    
    a) Add to Cart Action
    
    - User clicks "Add to Cart" button
    - Relevant route: **`@app.route('/add_to_cart/<int:product_id>', methods=['POST'])`**
    - Backend process:
        - Check if a cart exists in the session, create one if not
        - Add product to CartItem model or update quantity if already in cart
    - Frontend update: Cart icon updates to show number of items
    
    b) View Cart
    
    - User navigates to cart page
    - Relevant route: **`@app.route('/cart')`**
    - Data displayed: List of cart items (product name, quantity, price), total price
    - Interactions:
        - Update quantities
        - Remove items
        - "Proceed to Checkout" button
    
    3.3 Checkout Process
    
    a) Initiate Checkout
    
    - User clicks "Proceed to Checkout"
    - Relevant route: **`@app.route('/checkout', methods=['GET', 'POST'])`**
    - Process:
        - Display checkout form (shipping details, etc.)
        - User fills in required information
    
    b) Payment
    
    - User submits checkout form
    - Backend process:
        - Create Stripe checkout session
        - Relevant function: **`create_stripe_session()`**
    - User is redirected to Stripe payment page
    
    c) Payment Confirmation
    
    - User completes payment on Stripe
    - Stripe redirects user back to our site
    - Relevant route: **`@app.route('/checkout/success')`**
    
    3.4 Order Confirmation
    
    a) Order Creation
    
    - Backend process:
        - Create new Order in database
        - Create associated OrderItems
        - Clear user's cart
    - Relevant route: **`@app.route('/checkout/success')`**
    
    b) Confirmation Display
    
    - User sees order confirmation page
    - Data displayed: Order number, items purchased, total amount, shipping details
        

        

### 4. Admin Authentication

4.1

a) Login Process

- Relevant route: **`@app.route('/admin/login', methods=['GET', 'POST'])`**
- Process:
    - Admin enters password
    - System validates the password
    - If correct, sets **`admin_logged_in`** session variable to True

b) Authentication Middleware

The Authentication Middleware is designed to protect admin routes by ensuring that only authenticated administrators can access them. It acts as a gatekeeper for all admin-related functionalities.

- The **`@admin_required`** decorator  checks for the presence and value of the **`admin_logged_in`**key in the session.
- This session variable is set to **`True`** when an admin successfully logs in.
- If **`admin_logged_in`** is **`True`**, the middleware allows the request to proceed to the protected route.
- If **`admin_logged_in`** is **`False`** or not present, the middleware redirects to the login page.
- Session-based: This method relies on Flask sessions, which are cryptographically signed.
- Server-side validation: The check happens on the server, preventing client-side tampering.
- No sensitive data: The session only stores a boolean flag, not sensitive admin credentials.

4.2 Viewing Orders

a) Order Dashboard

- Admin accesses the order management dashboard
- Relevant route: **`@app.route('/admin/orders')`**
- Data displayed:
    - List of orders with key information (Order ID, Date, Customer, Total, Status)
    - Pagination of orders
- Filtering:
    - Describe the status filter checkboxes (paid, processing, shipped, delivered)
    - Filtering holds the value from the checkbox in request.args in URL and sends the query to the database to retrieve orders with selected statuses of the checkbox.  Sending those orders back to order.html to be displayed by the table.
- Status Update Process
- Admin selects new status from dropdown on order list or detail page
- Relevant route: **`@app.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])`**
- Process:
    - System updates order status in the database
    - Page refreshes to show updated status

b) Order Details

- Admin clicks on an order to view details
- Relevant route: **`@app.route('/admin/orders/<int:order_id>')`**
- Data displayed:
    - Detailed order information
    - Customer details
    - Shipping information
    - List of ordered items
    - link to supplier for fulfillment

4.3 Log out

- All admin pages have simple logout button



### 5. Key Data Flows

This section outlines the primary ways data moves through our e-commerce application, focusing on critical processes that involve multiple components of the system.

a) Adding Items to Cart

- Trigger: User clicks "Add to Cart" button

- Data flow:
    1. Frontend sends POST request with product ID and quantity
    2. Backend (route: **`/add_to_cart/<int:product_id>`**) receives request
    3. Check if a cart exists in the session, create if not
    4. Query database to get product details
    5. Create or update CartItem in the database
    6. Update session with new cart information
    7. Send response to frontend (success/failure, updated cart data)



b) Updating Cart

- Trigger: User changes quantity or removes item in cart view

- Data flow:
    1. JavaScript event listeners detect changes in quantity inputs or clicks on remove buttons
    2. JavaScript function prepares updated cart data (product IDs, new quantities)
    3. AJAX request sent to backend with updated cart information
    4. Backend (route: **`/update_cart`**) processes request
    5. Update CartItem entries in the database
    6. Recalculate cart totals
    7. Send JSON response to frontend with updated cart data
    8. JavaScript updates the DOM to reflect new cart state without page reload



c) Cart Persistence

1. Data Flow for Cart Persistence:
    
    a) Creating a New Cart:
    
    - When a user adds their first item to the cart:
        1. Generate a unique cart_id (e.g., using UUID)
        2. Store this cart_id in the session: **`session['cart_id'] = cart_id`**
        3. Create CartItem entries in the database with this cart_id
    
    b) Retrieving an Existing Cart:
    
    - When a user returns to the site:
        1. Check if a cart_id exists in the session
        2. If it exists, query the database for CartItems with this cart_id
        3. If no cart_id in session, check for recent CartItems in the database associated with the user's session or account (if logged in)
    
    5.2 Order Creation
    
    a) Initiating Checkout
    
    - Trigger: User clicks "Proceed to Checkout"
    - Data flow:
        1. Frontend sends request to initiate checkout
        2. Backend (route: **`/checkout`**) prepares order summary
        3. Retrieve cart items from database
        4. Calculate total amount
        5. Generate Stripe checkout session
        6. Send Stripe session ID to frontend
    
    b) Processing Payment
    
    - Trigger: User completes payment on Stripe
    - Data flow:
        1. Stripe redirects to success URL with session ID
        2. Backend (route: **`/checkout/success`**) receives request
        3. Verify Stripe session
        4. Create new Order entry in database
        5. Create OrderItem entries for each cart item
        6. Create ShippingDetails entry
        7. Clear user's cart (delete CartItems, clear session cart data)
        8. Go to order_confirmatio.html
        
        5.3 Order Status Updates
        
        Admin Updates Order Status
        
        - Trigger: Admin changes order status in dashboard
        - Data flow:
            1. Admin selects new status from dropdown menu
            2. Send selected statuses to backend through request.args in urls
            3. Backend (route: **`/admin/orders/<int:order_id>/update_status`**) receives request
            4. Update Order status in database
            5. Send orders with selected statuses back to frontend
    

import frappe
from frappe import auth

@frappe.whitelist(allow_guest=True)
def login(email, pwd):
    try:
        # Check if user exists with provided email
        user = frappe.db.get_value('User', {'email': email}, 'name')
        if not user:
            frappe.local.response["message"] = {
                "success_key": 0,
                "message": "User with provided email does not exist!"
            }
            frappe.local.response["http_status_code"] = 404
            return
        
        # Set the user in frappe session to the user retrieved
        frappe.local.login_manager = auth.LoginManager()
        frappe.local.login_manager.authenticate(user=user, pwd=pwd)
        frappe.local.login_manager.post_login()

    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": "Authentication Error! Invalid email or password."
        }
        frappe.local.response["http_status_code"] = 401
        return

    # Generate API key and secret for the authenticated user
    api_generate = generate_keys(frappe.session.user)
    user_doc = frappe.get_doc('User', frappe.session.user)

    frappe.local.response.pop("default_route", None)  # Removes 'default_route' if it exists, does nothing if it doesn't
    frappe.local.response.pop("home_page", None)      # Removes 'home_page' if it exists, does nothing if it doesn't
    frappe.local.response["message"] = {
        "success_key": 1,
        "message": "Authentication success",
        "sid": frappe.session.sid,
        #"api_key": user_doc.api_key,
        #"api_secret": api_generate, 
        # /***** Only for debug ****/
        # "data": user_doc,
        # /***** Only for debug ****/
        "first_name": user_doc.first_name,
        #"email": user_doc.email
    }

   
    return

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret

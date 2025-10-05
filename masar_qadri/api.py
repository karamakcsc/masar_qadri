import frappe

@frappe.whitelist()
def get_user_pos_profiles():
    """Return all POS Profiles assigned to the current user."""
    user = frappe.session.user

    profiles = frappe.db.get_all(
        "POS Profile User",
        filters={"user": user},
        pluck="parent"
    )

    return profiles

# @frappe.whitelist()    ## Execute daily in hooks
# def management_notification(): 
#     management = frappe.db.sql("""
#                         SELECT so1.company , so1.customer ,so1.customer_name , so1.transaction_date 
#                         FROM `tabSales Order` so1
#                         LEFT JOIN `tabSales Order` so2 
#                             ON so1.customer = so2.customer 
#                             AND so2.delivery_date > so1.delivery_date
#                         WHERE DATEDIFF(CURRENT_DATE() , so1.transaction_date) = 180 and so2.name IS NULL
#                         GROUP BY so1.customer
#                         """ , as_dict = 1 )
#     for m in management: 
#         management_email = frappe.db.get_value('Customer' , m.customer , 'custom_email')
#         if management_email is not None:
#             frappe.sendmail(
#                 recipients=management_email,
#                 subject='Last Order Notification',
#                 message=f"Dear {m.customer_name},<br>This is a notification that you have not placed any orders for the last 180 days.<br> Best regards,<br><b>{m.company}</b>",
#                 reference_doctype='Customer',
#                 reference_name=m.customer
#             )
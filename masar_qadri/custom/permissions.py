import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return None

    user_warehouse = frappe.db.get_value("Warehouse", {"custom_user": user}, "name")
    if not user_warehouse:
        return "1=2"

    return f"""
        (`tabStock Entry`.from_warehouse = '{user_warehouse}'
         OR `tabStock Entry`.custom_target_location = '{user_warehouse}')
    """


def has_permission(doc, user):
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return True

    user_warehouse = frappe.db.get_value("Warehouse", {"custom_user": user}, "name")
    if not user_warehouse:
        return False

    if (doc.from_warehouse == user_warehouse) or (doc.custom_target_location == user_warehouse):
        return True

    return False

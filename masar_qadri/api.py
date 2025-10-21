import frappe

@frappe.whitelist()
def get_user_pos_profiles():
    user = frappe.session.user

    profiles = frappe.get_all(
        "POS Profile User",
        filters={"user": user},
        pluck="parent"
    )

    if not profiles:
        profiles = frappe.get_all("POS Profile", pluck="name")

    return profiles

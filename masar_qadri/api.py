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

    # Optional: also include a direct user.pos_profile field if you use it
    if not profiles and frappe.db.has_column("User", "pos_profile"):
        profile = frappe.db.get_value("User", user, "pos_profile")
        if profile:
            profiles = [profile]

    return profiles

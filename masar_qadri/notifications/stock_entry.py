import frappe
from frappe.desk.doctype.notification_log.notification_log import make_notification_log


def stock_entry_notification(doc, method=None):
    notify_stock_entry_transfer(doc)


def notify_stock_entry_transfer(doc):
    """Notify target warehouse recipients and role-based users when stock is transferred"""
    if doc.docstatus != 1 or doc.stock_entry_type != "Material Transfer" or doc.outgoing_stock_entry:
        return

    subject = f"Stock Transfer {doc.name}: {doc.from_warehouse or 'N/A'} → {doc.to_warehouse or 'N/A'}"
    message = f"""
    <b>Stock Transfer:</b> {doc.name}<br>
    <b>From Warehouse:</b> {doc.from_warehouse or 'N/A'}<br>
    <b>To Warehouse:</b> {doc.to_warehouse or 'N/A'}<br>
    <b>Date:</b> {doc.posting_date}<br>
    <b>Total Qty:</b> {doc.total_outgoing_qty or 0}<br>
    <b>Company:</b> {doc.company or 'N/A'}<br>
    <b>Transferred By:</b> {doc.owner or 'System'}<br>
    """

    recipients = frappe.db.get_all(
        "Warehouse",
        filters={"name": doc.to_warehouse},
        pluck="custom_user"
    )

    role_recipients = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["Stock Manager"]]},
        pluck="parent"
    )

    all_recipients = list(set((recipients or []) + (role_recipients or [])))

    if not all_recipients:
        frappe.log_error(
            f"No notification recipients found for warehouse {doc.to_warehouse}",
            "Stock Entry Transfer Notification"
        )
        return

    make_notification_log(
        subject=subject,
        for_users=all_recipients,
        type="Alert",
        document_type="Stock Entry",
        document_name=doc.name,
    )

    frappe.sendmail(
        recipients=all_recipients,
        subject=subject,
        message=message,
    )

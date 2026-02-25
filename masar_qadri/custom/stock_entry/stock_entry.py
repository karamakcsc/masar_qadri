import frappe
##

def on_submit(self, method):
    validate_original_se(self)
    set_se_transfer_status(self, "Complete")
    notify_stock_entry_transfer(self)
def on_cancel(self, method):
    set_se_transfer_status(self, "Pending")


def set_se_transfer_status(self, status):
    if self.outgoing_stock_entry:
        parent_se = frappe.get_value("Stock Entry", self.outgoing_stock_entry, "add_to_transit")

        if parent_se:
            frappe.db.set_value("Stock Entry", self.outgoing_stock_entry, "custom_transfer_status", status)

def validate_original_se(self):
    if not self.outgoing_stock_entry:
        return

    existing = frappe.get_all(
        "Stock Entry",
        filters={
            "docstatus": 1,
            "outgoing_stock_entry": self.outgoing_stock_entry,
            "name": ["!=", self.name],
        },
        limit=1
    )

    if existing:
        frappe.throw(
            f"A completed Stock Entry <b>{existing[0].name}</b> already exists for this transfer."
        )
        
    original_se = frappe.get_doc("Stock Entry", self.outgoing_stock_entry)

    original_items = {}
    for row in original_se.items:
        original_items[row.item_code] = original_items.get(row.item_code, 0) + (row.qty or 0)

    current_items = {}
    for row in self.items:
        current_items[row.item_code] = current_items.get(row.item_code, 0) + (row.qty or 0)

    if len(original_items) != len(current_items):
        frappe.throw(
            "Items count must match the original Stock Entry (grouped by Item Code)."
        )

    for item_code, original_qty in original_items.items():

        if item_code not in current_items:
            frappe.throw(
                f"Item <b>{item_code}</b> does not exist in the submitted Stock Entry."
            )

        entered_qty = current_items[item_code]

        if entered_qty != original_qty:
            frappe.throw(
                f"Quantity mismatch for item <b>{item_code}</b>.<br>"
                f"Original Total Qty: <b>{original_qty}</b><br>"
                f"Entered Total Qty: <b>{entered_qty}</b><br><br>"
                f"<b>Total quantity per item must match exactly.</b>"
            )

def notify_stock_entry_transfer(doc):
    """Notify target warehouse recipients and role-based users when stock is transferred"""
    if doc.docstatus != 1 or doc.purpose != "Material Transfer" or doc.outgoing_stock_entry:
        return

    subject = f"Stock Transfer {doc.name}: {doc.from_warehouse or 'N/A'} → {doc.to_warehouse or 'N/A'}"
    message = f"""
    <b>Stock Transfer:</b> {doc.name}<br>
    <b>From Warehouse:</b> {doc.from_warehouse or 'N/A'}<br>
    <b>To Warehouse:</b> {doc.to_warehouse or 'N/A'}<br>
    <b>Date:</b> {doc.posting_date}<br>
    <b>Total Qty:</b> {sum((x.qty or 0) for x in doc.items)}<br>
    <b>Company:</b> {doc.company or 'N/A'}<br>
    <b>Transferred By:</b> {doc.owner or 'System'}<br>
    """

    branch_emails = {
        "Abdali Mall - QH": "abdali@qadri.jo",
        "MM-QDR01 - QH": "mecca@qadri.jo",
        "JH-QDR01 - QH": "hussein@qadri.jo",
        "IR-QDR02 - QH": "irbid-city@qadri.jo",
        "Arabilla-QDR01 - QH": "irbid@qadri.jo",
        "ZQ-QDR03 - QH": "zarqa.bm@qadri.jo",
        "ZQ-QDR02 - QH": "zarqa2@qadri.jo",
        "ZQ-QDR01 - QH": "zarqa@qadri.jo"
    }

    role_recipients = ["warehous@qadri.jo", "logistics@qadri.jo"]

    branch_email = branch_emails.get(doc.to_warehouse, None)

    all_recipients = list(
        set(role_recipients + ([branch_email] if branch_email else []))
    )

    if not all_recipients:
        frappe.log_error(
            f"No notification recipients found for warehouse {doc.to_warehouse}",
            "Stock Entry Transfer Notification"
        )
        return

    frappe.sendmail(
        recipients=all_recipients,
        subject=subject,
        message=message,
    )


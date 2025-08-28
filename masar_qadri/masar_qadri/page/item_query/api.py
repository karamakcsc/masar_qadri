import frappe

@frappe.whitelist()
def get_item_from_barcode(barcode):
    """Get full item details from barcode"""
    try:
        item_code = frappe.db.get_value(
            "Item Barcode",
            {"barcode": barcode},
            "parent"
        )
        if not item_code:
            return None

        # Fetch full item with child tables (barcodes, attributes)
        item_doc = frappe.get_doc("Item", item_code)

        # Return dict instead of Document (safe for JSON)
        return item_doc.as_dict()
    except Exception as e:
        frappe.log_error(f"Error fetching item from barcode: {str(e)}")
        return None

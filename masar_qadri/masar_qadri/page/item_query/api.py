import frappe

@frappe.whitelist()
def get_item_from_barcode(barcode):
    """Get item code from barcode"""
    try:
        # Query the Item doctype directly for barcodes
        items = frappe.db.sql("""
            SELECT name 
            FROM `tabItem` 
            WHERE name IN (
                SELECT parent 
                FROM `tabItem Barcode` 
                WHERE barcode = %s
            )
            LIMIT 1
        """, (barcode,), as_dict=True)
        
        if items:
            return items[0].name
        else:
            return None
    except Exception as e:
        frappe.log_error(f"Error fetching item from barcode: {str(e)}")
        return None
import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters=None):
    if not filters.get("user"):
        frappe.throw("Please select a user to generate the report.")
    user = filters.get("user")
    sql = frappe.db.sql(f"""
        WITH opening AS (
            SELECT 
                tpos.period_start_date,
                tpos.pos_profile AS pp,
                tpos.`user`,
                tposd.mode_of_payment AS omop,
                SUM(tposd.amount) AS oamount
            FROM `tabPOS Opening Shift` tpos
            INNER JOIN `tabPOS Opening Shift Detail` tposd ON tpos.name = tposd.parent
            WHERE tpos.docstatus = 1 AND tpos.status = 'Open' AND tpos.`user` = '{user}'
            GROUP BY tposd.mode_of_payment
        ),
        final_amount AS (
            SELECT 
                tpi.name,
                tsip.mode_of_payment AS famop,
                SUM(tsip.amount) AS faamount
            FROM `tabSales Invoice` tpi
            INNER JOIN `tabSales Invoice Payment` tsip ON tpi.name = tsip.parent
            WHERE tpi.docstatus = 1
            GROUP BY tsip.mode_of_payment
        )
        SELECT 
            o.omop,
            o.oamount,
            (IFNULL(o.oamount, 0) + IFNULL(fa.faamount, 0)) AS final_amount
        FROM opening o
        INNER JOIN final_amount fa ON o.omop = fa.famop
    """)
    
    
    return sql

def get_columns():
    return [
        {"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 350},
        {"label": "Opening Amount", "fieldname": "opening_amount", "fieldtype": "Currency", "width": 350},
        {"label": "Total Amount", "fieldname": "expected_amount", "fieldtype": "Currency", "width": 350},
    ]
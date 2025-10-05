# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "width": 180},
        {"label": _("Mode of Payment"), "fieldname": "mode_of_payment", "fieldtype": "Link", "options": "Mode of Payment", "width": 180},
        {"label": _("Opening Amount"), "fieldname": "opening_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Closing Amount"), "fieldname": "closing_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Expected Amount"), "fieldname": "expected_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Difference"), "fieldname": "difference", "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):
    conditions = ""
    if filters.get("pos_profile"):
        conditions += f" AND pcs.pos_profile = '{filters.get('pos_profile')}'"
    from_date, to_date = filters.get("from_date"), filters.get("to_date")
    if from_date and to_date:
        conditions += f" AND pcs.posting_date BETWEEN '{from_date}' AND '{to_date}'"

    data = frappe.db.sql(f"""
        SELECT
            pcs.posting_date,
            pcs.pos_profile,
            pr.mode_of_payment,
            SUM(pr.opening_amount) AS opening_amount,
            SUM(pr.closing_amount) AS closing_amount,
            SUM(pr.expected_amount) AS expected_amount,
            SUM(pr.difference) AS difference
        FROM `tabPOS Closing Shift` pcs
        LEFT JOIN `tabPOS Closing Shift Detail` pr
            ON pr.parent = pcs.name
        WHERE pcs.docstatus = 1
        {conditions}
        GROUP BY pcs.posting_date, pcs.pos_profile, pr.mode_of_payment
        ORDER BY pcs.posting_date DESC, pcs.pos_profile
    """, filters, as_dict=True)

    return data
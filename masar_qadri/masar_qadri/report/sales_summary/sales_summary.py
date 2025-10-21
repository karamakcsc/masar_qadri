# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{"label": _("Sales Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 200},
		{"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "width": 250},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
		{"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Float", "width": 200},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 200},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 200},
	]


def get_data(filters):
	conditions = " 1=1 "

	if filters.get("pos_profile"):
		conditions += f" AND tpi.pos_profile = '{filters.get('pos_profile')}'"
	if filters.get("customer"):
		conditions += f" AND tpi.customer = '{filters.get('customer')}'"
	if filters.get("sales_invoice"):
		conditions += f" AND tpi.name = '{filters.get('sales_invoice')}'"
	_from, to = filters.get("from_date"), filters.get("to_date")
	if _from and to:
		conditions += f" AND tpi.posting_date BETWEEN '{_from}' AND '{to}'"

	data = frappe.db.sql(
		f"""
		SELECT
			tpi.name,
			tpi.pos_profile,
			tpi.customer,
			tpi.total_qty AS total_qty,
			tpi.grand_total AS grand_total,
			tpi.posting_date
		FROM `tabSales Invoice` tpi
		WHERE tpi.docstatus = 1 AND {conditions}
		ORDER BY tpi.posting_date DESC
		"""
	)

	return data
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
		{"label": _("POS Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "POS Invoice", "width": 150},
		{"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "width": 150},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": _("Total Quantity"), "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
		{"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 140},
		{"label": _("Mode of Payment"), "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 150},
		{"label": _("Mode of Payment Amount"), "fieldname": "mode_of_payment_amount", "fieldtype": "Currency", "width": 180},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
	]


def get_data(filters):
	conditions = " 1=1 "

	if filters.get("pos_profile"):
		conditions += f" AND pos.pos_profile = '{filters.get('pos_profile')}'"
	if filters.get("customer"):
		conditions += f" AND pos.customer = '{filters.get('customer')}'"
	_from, to = filters.get("from_date"), filters.get("to_date")
	if _from and to:
				conditions += f" AND pos.posting_date BETWEEN '{_from}' AND '{to}'"
	if filters.get("mode_of_payment"):
		conditions += f" AND pos.mode_of_payment = '{filters.get('mode_of_payment')}'"
	if filters.get("pos_inv"):
		conditions += f" AND pos.name = '{filters.get('pos_inv')}'"

	data = frappe.db.sql(
		f"""
		SELECT
			pos.name,
			pos.pos_profile,
			pos.customer,
			pos.total_qty AS total_qty,
			pos.grand_total AS total_amount,
			payment.mode_of_payment,
   			payment.base_amount AS mode_of_payment_amount,
			pos.posting_date
		FROM `tabPOS Invoice` pos
		LEFT JOIN `tabSales Invoice Payment` payment ON payment.parent = pos.name
		WHERE pos.docstatus = 1 AND {conditions}
		GROUP BY pos.name, pos.pos_profile, pos.customer, payment.mode_of_payment, pos.posting_date
		ORDER BY pos.posting_date DESC
		"""
	)

	return data

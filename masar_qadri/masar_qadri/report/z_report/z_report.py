# Copyright (c) 2025, KCSC
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
	columns = [
		{"label": _("Period Start"), "fieldname": "period_start_date", "fieldtype": "Datetime", "width": 180},
  		{"label": _("Period End"), "fieldname": "period_end_date", "fieldtype": "Datetime", "width": 180},
		{"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Data", "width": 165},
		{"label": _("Mode of Payment"), "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 150},
		{"label": _("Opening Amount"), "fieldname": "opening_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Closing Amount"), "fieldname": "closing_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Net Expected"), "fieldname": "net_expected", "fieldtype": "Currency", "width": 120},
		{"label": _("Tax Amount"), "fieldname": "tax_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Expected Amount"), "fieldname": "expected_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Difference"), "fieldname": "difference", "fieldtype": "Data", "width": 120},
		# {"label": _("Total Refunds"), "fieldname": "total_refunds", "fieldtype": "Currency", "width": 120},
		# {"label": _("Total Discounts"), "fieldname": "total_discounts", "fieldtype": "Currency", "width": 120},
	]
	return columns


def get_data(filters):
	conditions = ""
	if filters.get("pos_profile"):
		conditions += f" AND tpcs.pos_profile = '{filters.get('pos_profile')}'"
	from_date, to_date = filters.get("from_date"), filters.get("to_date")
	if from_date and to_date:
		conditions += f" AND tpcs.posting_date BETWEEN '{from_date}' AND '{to_date}'"

	data = frappe.db.sql(f"""
		SELECT 
			tpcs.name AS shift_name,
			tpcs.period_start_date,
			tpcs.period_end_date,
			tpcs.pos_profile,
			tpcsd.mode_of_payment,
			tpcsd.opening_amount,
			tpcsd.closing_amount,
			tpcsd.expected_amount,
			tpcsd.difference
		FROM `tabPOS Closing Shift` tpcs
		LEFT JOIN `tabPOS Closing Shift Detail` tpcsd ON tpcsd.parent = tpcs.name
		WHERE tpcs.docstatus = 1
		{conditions}
		ORDER BY tpcs.posting_date DESC, tpcs.pos_profile
	""", as_dict=True)

	for d in data:
		d["net_expected"] = flt(d["expected_amount"]) / 1.16
		d["tax_amount"] = flt(d["expected_amount"]) - d["net_expected"]
		d["difference"] = str(d["difference"])

		# d["total_refunds"] = get_total_refunds(d.get("shift_name"))
		# d["total_discounts"] = get_total_discounts(d.get("shift_name"))

	return data


# def get_total_refunds(shift_name):
# 	total_refund = frappe.db.sql("""
# 		SELECT SUM(ABS(tsir.grand_total))
# 		FROM `tabSales Invoice Reference` tsir
# 		WHERE tsir.parent = %s
# 		AND tsir.grand_total < 0
# 	""", (shift_name,))[0][0] or 0
# 	return flt(total_refund)


# def get_total_discounts(shift_name):
# 	invoice_names = frappe.db.get_all(
# 		"Sales Invoice Reference",
# 		filters={"parent": shift_name},
# 		pluck="pos_invoice"
# 	)

# 	if not invoice_names:
# 		return 0

# 	total_discount = 0
# 	for inv in invoice_names:
# 		invoice = frappe.get_doc("Sales Invoice", inv)

# 		additional_discount = flt(invoice.get("additional_discount_amount", 0))

# 		item_discount = sum(flt(i.get("discount_amount", 0)) for i in invoice.get("items", []))

# 		total_discount += additional_discount + item_discount

# 	return flt(total_discount)

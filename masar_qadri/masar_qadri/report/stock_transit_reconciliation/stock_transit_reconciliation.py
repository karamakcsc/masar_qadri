# Copyright (c) 2026, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return columns(), data(filters), None

def data(filters):
	conditions = " 1=1 "
	if filters.get("stock_entry"):
		conditions += f" AND co.name = '{filters.get('stock_entry')}' "
	from_date, to_date = filters.get("from_date"), filters.get("to_date")
	if from_date and to_date:
		conditions += f" AND co.posting_date BETWEEN '{from_date}' AND '{to_date}'"
		
	# co (Check Out). ci (Check In) 
	sql = frappe.db.sql(f"""
		SELECT
			co.name AS check_out_se,
			SUM(coi.qty) AS check_out_qty,
			GROUP_CONCAT(DISTINCT ci.name ORDER BY ci.name SEPARATOR ', ') AS check_in_entries,
			SUM(cii.qty) AS total_check_in_qty,
			COUNT(DISTINCT ci.name) AS check_in_count,
			CASE
				WHEN COUNT(DISTINCT ci.name) = 0 THEN 'Not Correct'
				WHEN SUM(coi.qty) = SUM(cii.qty) AND COUNT(DISTINCT ci.name) = 1 THEN 'Correct'
				WHEN SUM(coi.qty) = SUM(cii.qty) AND COUNT(DISTINCT ci.name) > 1 THEN 'Correct (Multiple Check-ins)'
				ELSE 'Not Correct'
			END AS reconciliation_status
		FROM `tabStock Entry` co
		INNER JOIN `tabStock Entry Detail` coi
			ON co.name = coi.parent
		LEFT JOIN `tabStock Entry` ci
			ON ci.outgoing_stock_entry = co.name
			AND ci.docstatus IN (0, 1)
		LEFT JOIN `tabStock Entry Detail` cii
			ON ci.name = cii.parent
			AND cii.item_code = coi.item_code
		WHERE
			{conditions}
			AND co.docstatus IN (0, 1)
			AND co.purpose = 'Material Transfer'
			AND (co.outgoing_stock_entry IS NULL OR co.outgoing_stock_entry = '')
		GROUP BY
			co.name
		ORDER BY
			co.name;
	""",as_dict=True)

	return sql

def columns():
    return [
		{"label": "Check Out Stock Entry", "fieldname": "check_out_se", "fieldtype": "Link", "options": "Stock Entry", "width": 200},
		{"label": "Check Out Qty", "fieldname": "check_out_qty", "fieldtype": "Float", "width": 120},
		{"label": "Check In Stock Entries", "fieldname": "check_in_entries", "fieldtype": "Data", "width": 250},
		{"label": "Total Check In Qty", "fieldname": "total_check_in_qty", "fieldtype": "Float", "width": 150},
		{"label": "Number of Check Ins", "fieldname": "check_in_count", "fieldtype": "Int", "width": 130},
		{"label": "Reconciliation Status", "fieldname": "reconciliation_status", "fieldtype": "Data", "width": 180},
	]

# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return columns(), data(filters), None

def data(filters):
	conditions = " 1=1 "
 
	if filters.get("sales_invoice"):
		conditions += f" AND tsi.name = '{filters.get('sales_invoice')}' "
	if filters.get("pos_profile"):
		conditions += f" AND tsi.pos_profile = '{filters.get('pos_profile')}' "
	if filters.get("customer"):
		conditions += f" AND tsi.customer = '{filters.get('customer')}' "
	_from, to = filters.get("from_date"), filters.get("to_date")
	if _from and to:
		conditions += f" AND tsi.posting_date BETWEEN '{_from}' AND '{to}' "


	sql = frappe.db.sql(f"""
        SELECT
			tsi.name AS `Original Invoice`,
			tsi.posting_date AS `Original Posting Date`,
			tsi.pos_profile AS `Original POS Profile`,
			tsi.customer AS `Original Customer`,
			tsi.total_qty AS `Original Total Qty`,
			tsi.net_total AS `Original Net Total`,
			tsi.total_taxes_and_charges AS `Original Taxes`, 
			tsi.grand_total AS `Original Grand Total`,
			GROUP_CONCAT(DISTINCT tst.sales_person) AS `Original Sales Person`, 
			tsi2.name AS `Return Invoice`,
			tsi2.posting_date AS `Return Posting Date`,
			tsi2.pos_profile AS `Return POS Profile`,
			tsi2.customer AS `Return Customer`,
			tsi2.total_qty AS `Return Total Qty`,
			tsi2.net_total AS `Return Net Total`,
			tsi2.total_taxes_and_charges AS `Return Taxes`, 
			tsi2.grand_total AS `Return Grand Total`,
			GROUP_CONCAT(DISTINCT tst2.sales_person) AS `Return Sales Person`
		FROM `tabSales Invoice` tsi
		INNER JOIN `tabSales Invoice` tsi2 ON tsi.name = tsi2.return_against
		LEFT JOIN `tabSales Team` tst ON tst.parent = tsi.name
		LEFT JOIN `tabSales Team` tst2 ON tst2.parent = tsi2.name
		WHERE {conditions} AND tsi.docstatus = 1 AND tsi2.docstatus = 1
		GROUP BY tsi.name, tsi2.name
	""")
    
	return sql


def columns():
    return [
		"Original Invoice:Link/Sales Invoice:200",
		"Original Posting Date:Date:150",
		"Original POS Profile:Data:200",
		"Original Customer:Data:200",
		"Original Total Qty:Int:200",
		"Original Net Total:Currency:200",
		"Original Taxes:Currency:150",
		"Original Grand Total:Currency:200",
		"Original Sales Person:Data:200",
		"Return Invoice:Link/Sales Invoice:200",
		"Return Posting Date:Date:150",
		"Return POS Profile:Data:200",
		"Return Customer:Data:200",
		"Return Total Qty:Float:200",
		"Return Net Total:Currency:200",
		"Return Taxes:Currency:150",
		"Return Grand Total:Currency:200",
		"Return Sales Person:Data:200",
	]

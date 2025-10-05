# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, qb
from frappe.query_builder import Criterion

from erpnext import get_company_currency


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	entries = get_entries(filters)
	item_details = get_item_details()
	data = []

	company_currency = get_company_currency(filters.get("company"))
 
	total_qty = total_amount = total_upt = total_utv = count = 0

	for d in entries:
		if d.stock_qty > 0 or filters.get("show_return_entries", 0):
			qty = d.stock_qty
			amount = d.base_net_amount
			upt = qty / 1  # since one POS Invoice is considered one transaction
			utv = amount / qty if qty else 0
			data.append(
				[
					d.name,
					d.sales_person,
					d.customer,
					d.warehouse,
					d.posting_date,
					d.item_code,
					item_details.get(d.item_code, {}).get("item_group"),
					item_details.get(d.item_code, {}).get("description_code"),
					qty,
					amount,
					upt,
					utv,
					d.allocated_percentage,
					(qty * d.allocated_percentage / 100),
					company_currency,
				])
			total_qty += qty
			total_amount += amount
			total_upt += upt
			total_utv += utv
			count += 1

	if count > 0:
		avg_upt = total_upt / count
		avg_utv = total_utv / count

		# Add a visual separator (optional)
		data.append([""] * len(columns))

		# Add averages row with label and values
		avg_row = [""] * len(columns)
		avg_row[7] = _("Averages")  # place label under Description Code column
		avg_row[10] = avg_upt
		avg_row[11] = avg_utv
		data.append(avg_row)

	return columns, data


def get_columns(filters):

	columns = [
		{
			"label": _("POS Invoice"),
			"options": "POS Invoice",
			"fieldname": "pos_invoice",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Sales Person"),
			"options": "Sales Person",
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Customer"),
			"options": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Warehouse"),
			"options": "Warehouse",
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"width": 140,
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 140},
		{
			"label": _("Item Code"),
			"options": "Item",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Item Group"),
			"options": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Link",
			"width": 140,
		},
		{"label": _("Description Code"), "fieldname": "description_code", "fieldtype": "Data", "width": 200},
		{"label": _("Invoice Total Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 140},
		{
			"label": _("Amount"),
			"options": "currency",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		{"label": _("UPT"), "fieldname": "upt", "fieldtype": "Float", "width": 100},
        {"label": _("ATV"), "fieldname": "utv", "fieldtype": "Currency", "width": 120},
		{
			"label": _("Currency"),
			"options": "Currency",
			"fieldname": "currency",
			"fieldtype": "Link",
			"hidden": 1,
		},
	]

	return columns


def get_entries(filters):
    date_field = "posting_date"
    qty_field = "qty"

    conditions, values = get_conditions(filters, date_field)

    entries = frappe.db.sql(
        f"""
        SELECT
            dt.name, dt.customer, dt.{date_field} as posting_date,
            dt_item.item_code, st.sales_person, st.allocated_percentage,
            dt_item.warehouse, dt_item.stock_qty,
            dt_item.base_net_amount
        FROM
            `tabPOS Invoice` dt,
            `tabPOS Invoice Item` dt_item,
            `tabSales Team` st
        WHERE
            st.parent = dt.name
            AND dt.name = dt_item.parent
            AND st.parenttype = 'POS Invoice'
            AND dt.docstatus = 1
            {conditions}
        ORDER BY st.sales_person, dt.name DESC
        """,
        tuple(values),
        as_dict=1,
    )

    return entries



def get_conditions(filters, date_field):
	conditions = [""]
	values = []

	for field in ["company", "customer"]:
		if filters.get(field):
			conditions.append(f"dt.{field}=%s")
			values.append(filters[field])

	if filters.get("sales_person"):
		lft, rgt = frappe.get_value("Sales Person", filters.get("sales_person"), ["lft", "rgt"])
		conditions.append(
			f"exists(select name from `tabSales Person` where lft >= {lft} and rgt <= {rgt} and name=st.sales_person)"
		)

	if filters.get("from_date"):
		conditions.append(f"dt.{date_field}>=%s")
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append(f"dt.{date_field}<=%s")
		values.append(filters["to_date"])

	items = get_items(filters)
	if items:
		conditions.append("dt_item.item_code in (%s)" % ", ".join(["%s"] * len(items)))
		values += items
	else:
		# return empty result, if no items are fetched after filtering on 'item group' and 'brand'
		conditions.append("dt_item.item_code = Null")

	return " and ".join(conditions), values


def get_items(filters):
	item = qb.DocType("Item")

	item_query_conditions = []
	if filters.get("item_group"):
		# Handle 'Parent' nodes as well.
		item_group = qb.DocType("Item Group")
		lft, rgt = frappe.db.get_all(
			"Item Group", filters={"name": filters.get("item_group")}, fields=["lft", "rgt"], as_list=True
		)[0]
		item_group_query = (
			qb.from_(item_group)
			.select(item_group.name)
			.where((item_group.lft >= lft) & (item_group.rgt <= rgt))
		)
		item_query_conditions.append(item.item_group.isin(item_group_query))

	items = qb.from_(item).select(item.name).where(Criterion.all(item_query_conditions)).run()
	return items


def get_item_details():
	item_details = {}
	for d in frappe.db.sql("""SELECT `name`, item_name, `item_group`, custom_description_code AS description_code FROM `tabItem`""", as_dict=1):
		item_details.setdefault(d.name, d)

	return item_details

import frappe

def before_submit(self, method):
    populate_sales_team(self)

def populate_sales_team(self):
    if not self.items:
        return

    sales_person_list = [item.custom_sales_person for item in self.items if item.custom_sales_person]

    existing_sales_persons = [d.sales_person for d in self.sales_team]

    for sp in set(sales_person_list):
        if sp not in existing_sales_persons:
            item_net_amount = sum(i.net_amount for i in self.items if i.custom_sales_person == sp)
            if self.net_total and item_net_amount:
                contribution = round((item_net_amount / self.net_total) * 100, 2)
            else:
                contribution = 0

            sp_entry = {
                "sales_person": sp,
                "allocated_percentage": contribution,
                "allocated_amount": item_net_amount,
            }

            self.append("sales_team", sp_entry)
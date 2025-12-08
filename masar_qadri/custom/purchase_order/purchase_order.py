import frappe


def validate(self, method):
    set_supplier_dimension(self)
def on_submit(self, method):
    validate_rate(self)


def set_supplier_dimension(self):
    if self.supplier:
        for item in self.items:
            item.internal_supplier = self.supplier
            
def validate_rate(self):
    if self.items:
        for item in self.items:
            if item.rate <= 0:
                frappe.throw(f"Rate must be greater than zero for item {item.item_code} in row {item.idx}.")
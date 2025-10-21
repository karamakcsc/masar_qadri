import frappe
from json import loads
from re import sub
from datetime import datetime

def validate(self , method ): 
    rename_with_description(self)
    generate_barcode(self)
    

@frappe.whitelist()
def description_property(self):
    if not isinstance(self, dict):
        self = frappe._dict(loads(self))
    if self.get('has_variants') == 0: 
       return True 
    if len(self.get('attributes' , [])) != 0 : 
        for att in self.get('attributes'): 
            if att.get('attribute') == 'Description':
                return False
    return True 


def rename_with_description(self):
    if self.has_variants == 1: 
        i = frappe.qb.DocType(self.doctype)
        variants = (
                frappe.qb.from_(i)
                .select(i.name , i.custom_description_code)
                .where(i.variant_of == self.name )
                .run(as_dict= True )
        )
        if len(variants) != 0 :
            if len(variants) < 10: 
                rename_variants(self , variants )
            else: 
                frappe.enqueue(
                    "masar_qadri.custom.item.item.rename_variants",
                    self=self,
                    variants=variants
                )
                frappe.msgprint("Variant Items has been queued.",
								indicator= "orange",
                                alert=True
							)
            
            
            
def rename_variants(self , variants ):
    abbr_list = list()
    new_name = ''
    new_des_code = self.custom_description_code
    for var in variants:
        if var.custom_description_code != new_des_code:
            splitted_var = (var.name).split('-')
            var_doc = frappe.get_doc(self.doctype , var.name)
            for a in var_doc.attributes:
                abbr = frappe.db.get_value(
                    'Item Attribute Value' ,
                    fieldname=["abbr"], 
                    filters={'parent':a.attribute , 'attribute_value': a.attribute_value }
                )
                abbr_list.append(abbr)
            privious_description_code_list = [des for des in splitted_var if des not in  abbr_list ]
            if len(privious_description_code_list) != 0: 
                new_name =sub(privious_description_code_list[0] , self.custom_description_code,var.name)
                var_doc.custom_description_code = new_des_code
                var_doc.save()
            
                if (var.name  !=  new_name):
                    frappe.rename_doc(
                        doctype=self.doctype,
                        old= var.name, 
                        new= new_name, 
                        show_alert=True
                        )
                frappe.db.commit()
                
def generate_barcode(self):
    if len(self.barcodes) != 0:
        return
    
    current_year = datetime.now().year
    existing_barcodes_sql = frappe.db.sql("""
            SELECT MAX(tib.barcode) AS `barcode`
            FROM `tabItem Barcode` tib
            WHERE tib.barcode LIKE %s
            """, (f"{current_year}%"), as_dict=True)
    if existing_barcodes_sql and existing_barcodes_sql[0] and existing_barcodes_sql[0]['barcode']:
        max_number = existing_barcodes_sql[0]['barcode']
        serial_num = int(max_number[4:])
        serial = "{:08d}".format(serial_num + 1)
        new_barcode = f"{current_year}{serial}"
    else:
        serial = "{:08d}".format(1)
        new_barcode = f"{current_year}{serial}"
    if new_barcode:
        self.append('barcodes', {
            "barcode": new_barcode
        })
    
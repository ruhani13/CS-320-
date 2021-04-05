# project: p2
# submitter: rarora23
# partner: none
# hours: 45

from zipfile import ZipFile, ZIP_DEFLATED
from io import TextIOWrapper
import json
import csv

class ZippedCSVReader:
    def __init__(self, filename):
        self.zipfile = filename
        self.paths = []
        with ZipFile(filename) as zf:
            for info in zf.infolist():
                self.paths.append(info.filename)
        sorted(self.paths)
        
    def load_json(self, filename):
        ret_dict = {}
        with ZipFile(self.zipfile) as zf:
            with zf.open(filename) as f:
                ret_dict = json.load(f)
        return ret_dict
    
    def rows(self, filename = None):
        ret_rows = []
        with ZipFile(self.zipfile) as zf:
                if not filename == None:
                    with zf.open(filename) as f:
                        tio = TextIOWrapper(f)
                        reader = csv.DictReader(tio)
                        for row in reader:
                            ret_rows.append(dict(row))
                else: #read all csv files
                    for filename in self.paths:
                        with zf.open(filename) as f:
                            tio = TextIOWrapper(f)
                            reader = csv.DictReader(tio)
                            for row in reader:
                                ret_rows.append(dict(row))
        return ret_rows

    
class Loan:
    def __init__(self, amount, purpose, race, income, decision):
        #self.keys = {"amount" : amount, "purpose" : purpose, "race" : race, "income" : income, "decision" : decision}
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.income = income
        self.decision = decision

    @property 
    def keys(self):
        return {k: getattr(self, k) for k in ["amount", "purpose" , "race" , "income" , "decision" ]}
      
                
    def __repr__(self):
         return f"Loan({self.amount}, {repr(self.purpose)}, {repr(self.race)}, {self.income}, {repr(self.decision)})"

    def __getitem__(self, lookup):        
        if lookup in self.keys:
            return self.keys[lookup]
        else:
            if lookup in self.keys.values():
                return 1
            else:
                return 0

def get_bank_names(reader):
    bank_list = []
    rows = reader.rows()
    for row in rows:
        bank = row["agency_abbr"]
        if bank not in bank_list:
            bank_list.append(bank)
    return sorted(bank_list)

class Bank:
    
    def __init__(self, name, reader) :
        self.name = name
        self.reader = reader
        
    def loans(self):
        dict_rows = self.reader.rows()
        loan_list = []
        for row in dict_rows:         
            if not self.name or row["agency_abbr"] == self.name:
                amount = int(row["loan_amount_000s"]) if row["loan_amount_000s"] != "" else 0
                purpose = row["loan_purpose_name"] if row["loan_purpose_name"] != "" else 0
                race = row["applicant_race_name_1"] if row["applicant_race_name_1"] != "" else 0
                income =  int(row["applicant_income_000s"]) if row["applicant_income_000s"] != "" else 0
                decision = "approve" if row["action_taken"] == 1 else "deny"
                new_loan = Loan(amount, purpose, race, income, decision)
                loan_list.append(new_loan)
        return loan_list  
    

class SimplePredictor():
    def __init__(self):
        self.applicants_approved = 0
        self.applicants_denied  = 0

    def predict(self, loan):
        if loan["purpose"] == "Refinancing":
            self.applicants_approved +=1
            return True
        else:
            self.applicants_denied +=1
            return False

    def get_approved(self):
        return self.applicants_approved

    def get_denied(self):
        return self.applicants_denied  
    
    
class DTree(SimplePredictor):
    def __init__(self, nodes):
        super().__init__()

        # a dict with keys: field, threshold, left, right
        # left and right, if set, refer to similar dicts
        self.root = nodes

    def dump(self, node=None, indent=0):
        if node == None:
            node = self.root

        if node["field"] == "class":
            line = "class=" + str(node["threshold"])
        else:
            line = node["field"] + " <= " + str(node["threshold"])
        print("  "*indent + line)
        if node["left"]:
            self.dump(node["left"], indent+1)
        if node["right"]:
            self.dump(node["right"], indent+1)
            
    def node_count(self, node=None, node_count = 1):
        if node == None:
            node = self.root
        if node["left"]:
            node_count  = self.node_count(node["left"], node_count+1)
        if node["right"]:
            node_count  = self.node_count(node["right"], node_count+1)
            
        return node_count
    
    def predict(self,loan,node = None):
        if node == None:
            node = self.root
        if node["field"] == "class":
            if node["threshold"] == 1:
                self.applicants_approved +=1
                return True
            else:
                self.applicants_denied +=1
                return False # base case
        if loan[node["field"]] <= node["threshold"]:
            return self.predict(loan, node["left"])
        if loan[node["field"]] > node["threshold"]:
            return self.predict(loan, node["right"]) # recursive case
                
    
    
def bias_test(bank, predictor, race_override):
    c1 = 0
    c2 = 0
    for loan in bank.loans(): 
        pred = predictor.predict(loan) 
        loan.race = race_override 
        over_ride = predictor.predict(loan)
        if pred != over_ride:
            c1 += 1  
        c2+=1   
    return c1/c2
   
     
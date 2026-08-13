import sys
import os
import csv

def resource_path(relative_path):
    """
    Takes in the relative_path of the file, and converts if needed to allow compiling.
    Should use whenever importing or reading a file stored in a directory.
    Try to change to _MEIPASS2 if having import errors.
    Args:
        relative_path (string): Relative path to file of interest.

    Returns:
        String: Correct path for use raw vs compiled.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

specimen_list_csv = resource_path("assets/delnorSpecimenList.csv")

typo_dict: dict = {
    "clcok": "clock",
    "clokc": "clock",
    "o'clcok": "o'clock",
    "o'clokc": "o'clock",
    "junciton": "junction",
    "heptaic": "hepatic"
}

acronym_dict: dict = {
    "gej": "gastroesophageal junction",
    "ge": "gastroesophageal",
    "ti": "terminal ileum",
    "bx": "biopsy",
    "bxs": "biopsies",
    "cxbx": "cervical biopsy",
    "cxbxs": "cervical biopsies",
    "lt": "left",
    "rt": "right",
    "cmfn": "centimeters from the nipple",
    "nme": "non-mass enhancement"
}

all_caps_list: list = [
    'leep', 'leep,',
    'roi', 'roi,',
    'ti', 'ti,',
    'mri', 'mri,'
]

all_lower_list: list = [
    'cm', 'cm,',
    'and', 'and,',
    'at', 'at,'
]

special_capitalization_dict: dict = {
    "o'clock": "O'Clock",
    "non-mass": "Non-Mass"
}

class SpecimenTemplates:
  
    def __init__(self):  # Establish core class elements  
        self.signout_template_file = specimen_list_csv
        self.specimen_dict = {}
        self.raw_to_dict()
           
    def raw_to_dict(self):  # Relate specimen type to codes as dict 
        temp_dict = {}
        with open(self.signout_template_file, "r") as csvfile:
            file = csv.reader(csvfile, dialect = 'excel')
            next(file, None)
            for row in file:
                specimen_name = row[0].lower().strip()
                specimen_type = row[1].strip()
                organ = row[2].strip()
                procedure = row[3].strip()
                gross_default = row[4].lower().strip()
                
                temp_dict[specimen_name] = specimen_type,organ,procedure,gross_default
        self.specimen_dict = temp_dict        
        return self.specimen_dict
    
    def specimen_type_to_procedures(self, specimen_name):
        
        self.same_specimen_type = []
        
        try:
            specimen_type_to_match = self.specimen_dict[specimen_name][0]
        except:
            print(f"ERROR in specimen_type_to_procedures: Specimen name ({specimen_name}) not found in the specimen list.")
            self.same_specimen_type = ["Biopsy","Excision","Resection"]
            return self.same_specimen_type
        
        self.same_specimen_type.append(self.specimen_dict[specimen_name][2])
        for item in self.specimen_dict:
            if self.specimen_dict[item][0] == specimen_type_to_match and self.specimen_dict[item][1] == self.specimen_dict[specimen_name][1]:
                if self.specimen_dict[item][2] not in self.same_specimen_type:
                    self.same_specimen_type.append(self.specimen_dict[item][2])
        
        if "Biopsy" not in self.same_specimen_type:
            self.same_specimen_type.append("Biopsy")
        if "Excision" not in self.same_specimen_type:
            self.same_specimen_type.append("Excision")
        if "Resection" not in self.same_specimen_type:
            self.same_specimen_type.append("Resection")
        
        self.same_specimen_type[1:] = sorted(self.same_specimen_type[1:])    
        return self.same_specimen_type
    
    def specimen_name_to_organ_and_procedure(self, specimen_name):
        
        self.specimen_organ_and_procedure = []
        
        try:
            specimen_info_list = self.specimen_dict[specimen_name]
        except:
            print(f"ERROR in specimen_name_to_organ_and_procedure: Specimen name ({specimen_name}) not found in the specimen list.")
            self.specimen_organ_and_procedure = ["", "Biopsy"]  
            return self.specimen_organ_and_procedure
        
        self.specimen_organ_and_procedure = specimen_info_list[1], specimen_info_list[2]
        return  self.specimen_organ_and_procedure

class SignoutCleanup:
        
    def __init__(self, template_dict):
        self.template_dict = template_dict
        self.typo_dict = typo_dict
        self.acronym_dict = acronym_dict
        self.all_caps_list = all_caps_list
        self.all_lower_list = all_lower_list
        self.special_cap_dict = special_capitalization_dict
    
    def fix_typos(self):
        typo_list = list(self.typo_dict)
        for key in self.template_dict:
            description_list = []
            description = self.template_dict[key][1]
            description_words = description.split(" ")
            for word in description_words:
                word = word.lower()
                if word in typo_list:
                    print(f"INFO: Corrected an identified typo: '{word}' corrected to '{self.typo_dict[word]}'")
                    description_list.append(self.typo_dict[word])
                else:
                    description_list.append(word)
                self.template_dict[key][1] = (" ").join(description_list)
                
    def expand_acronyms(self):
        acronym_list = list(self.acronym_dict)
        for key in self.template_dict:
            description_list = []
            description = self.template_dict[key][1]
            description_words = description.split(" ")
            for word in description_words:
                check_word = word.lower()
                if word in acronym_list:
                    print(f"INFO: Expanded an identified acronym: '{word}' corrected to '{self.acronym_dict[check_word]}'")
                    description_list.append(self.acronym_dict[word])
                else:
                    description_list.append(word)
                self.template_dict[key][1] = (" ").join(description_list)
    
    def handle_capitalization(self):
        uppercase_list = self.all_caps_list
        lowercase_list = self.all_lower_list
        for key in self.template_dict:
            description_list = []
            description = self.template_dict[key][1]
            description_words = description.split(" ")
            for word in description_words:
                check_word = word.lower()
                if check_word in uppercase_list:
                    description_list.append(word.upper())
                elif word in lowercase_list:
                    description_list.append(word.lower())
                else:
                    description_list.append(word.capitalize())
                self.template_dict[key][1] = (" ").join(description_list)
        
    def special_capitalization(self):
        special_cap_list = list(self.special_cap_dict)
        for key in self.template_dict:
            description_list = []
            description = self.template_dict[key][1]
            description_words = description.split(" ")
            for word in description_words:
                check_word = word.lower()
                if check_word in special_cap_list:
                    print(f"INFO: Found a special capitalization case: '{word}' corrected to '{self.special_cap_dict[check_word]}'")
                    description_list.append(self.special_cap_dict[check_word])
                else:
                    description_list.append(word)
                self.template_dict[key][1] = (" ").join(description_list)
    
    def remove_duplicate_words(self):
        pass
    
    def initial_cleanup(self):
        self.fix_typos()
        self.expand_acronyms()
        self.handle_capitalization()
        self.special_capitalization()
        return self.template_dict
           
def main():

    test_dict = {'A': ['Breast mastectomy', "Right breast stitch at 12 o'clcok clcok NME"], 'B': ['Breast, margin', 'Rt chest wall margin, stitch at new margin'], 'C': ['leep', 'leep stitch at 12 clock'], 'D': ['Breast mastectomy', "12 CM breast lesion"]}
    
    st = SpecimenTemplates()
    sc = SignoutCleanup(template_dict=test_dict)
    print(sc.initial_cleanup())

if __name__ == "__main__":
    main()
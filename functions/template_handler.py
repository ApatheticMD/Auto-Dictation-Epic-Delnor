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

synonym_dict: dict= {
    'none': [''],
    'adenoids': [''],
    'soft tissue': [''],
    'adrenal gland': [''],
    'ampulla': [''],
    'digit': [''],
    'extremity': [''],
    'anus': [''],
    'anastomosis': [''],
    'blood vessel': [''],
    'appendix': [''],
    'atrial appendage': [''],
    'bone': [''],
    'skin': [''],
    'bladder': [''],
    'body fluid': [''],
    'brain': [''],
    'branchial cleft cyst': [''],
    'breast': [''],
    'bronchus': [''],
    'joint': [''],
    'carina': [''],
    'colon': [''],
    'cervix': [''],
    'clot': [''],
    'conjunctiva': [''],
    'cornea': [''],
    'cul-de-sac': [''],
    'other': [''],
    'oral cavity': [''],
    'ovary': [''],
    'diaphragm': [''],
    'spine': [''],
    'pancreas': [''],
    'intestine': [''],
    'duodenum': ['duodenal'],
    'ear': [''],
    'endocervix': [''],
    'fallopian tube': [''],
    'endometrium': [''],
    'epidural space': [''],
    'epiglottis': [''],
    'esophagus': ['esophageal'],
    'eye': [''],
    'foreign body': [''],
    'foreskin': [''],
    'gallbladder': [''],
    'stomach': ['gastric'],
    'gastroesophageal junction': [''],
    'heart': [''],
    'hemorrhoids': [''],
    'hernia sac': [''],
    'hydrocele sac': [''],
    'vaginal opening': [''],
    'ileocecal valve': [''],
    'ileum': [''],
    'kidney': [''],
    'labia': [''],
    'lacrimal sac': [''],
    'larynx': [''],
    'lip': [''],
    'liver': [''],
    'lung': [''],
    'lymph node': [''],
    'sinonasal cavity': [''],
    'mediastinum': [''],
    'meninges': [''],
    'mesentery': [''],
    'muscle': [''],
    'nail': [''],
    'nasolacrimal duct': [''],
    'nerve': [''],
    'omentum': [''],
    'orbital cavity': [''],
    'ovary and fallopian tubes': [''],
    'parathyroid gland': [''],
    'parotid gland': [''],
    'penis': [''],
    'perianal region': [''],
    'pericardium': [''],
    'perineum': [''],
    'peritoneum': [''],
    'pharynx': [''],
    'pituitary gland': [''],
    'placenta': [''],
    'pleura': [''],
    'products of conception': [''],
    'prostate': [''],
    'prostate and bladder': [''],
    'rectum': [''],
    'retroperitoneum': [''],
    'salivary gland': [''],
    'scrotum': [''],
    'seminal vesicle': [''],
    'septum': [''],
    'serosa': [''],
    'sinus contents': [''],
    'small bowel': [''],
    'spermatocele': [''],
    'spleen': [''],
    'stoma': [''],
    'synovium': [''],
    'tooth': [''],
    'tendon': [''],
    'testis': [''],
    'thymus': [''],
    'thyroid gland': [''],
    'tongue': [''],
    'tonsil': [''],
    'trachea': [''],
    'umbilical cord': [''],
    'ureter': [''],
    'urethra': [''],
    'uterus': [''],
    'uvula': [''],
    'vagina': [''],
    'spermatic cord': [''],
    'vas deferens': [''],
    'vocal cord': [''],
    'vulva': [''],
    'pancreas, duodenum, and stomach': [''],
}

class SpecimenTemplates:
  
    def __init__(self):
        self.signout_template_file = specimen_list_csv
        self.specimen_dict = {}
        self.raw_to_dict()
           
    def raw_to_dict(self):
        temp_dict = {}
        with open(self.signout_template_file, "r") as csvfile:
            file = csv.reader(csvfile, dialect = 'excel')
            next(file, None)
            for row in file:
                specimen_name = row[0].lower().strip()
                specimen_type = row[1].lower().strip()
                organ = row[2].strip()
                procedure = row[3].lower().strip()
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
            self.same_specimen_type = ["biopsy","excision","resection"]
            return self.same_specimen_type
        
        self.same_specimen_type.append(self.specimen_dict[specimen_name][2])
        for item in self.specimen_dict:
            if self.specimen_dict[item][0] == specimen_type_to_match and self.specimen_dict[item][1] == self.specimen_dict[specimen_name][1]:
                if self.specimen_dict[item][2] not in self.same_specimen_type:
                    self.same_specimen_type.append(self.specimen_dict[item][2])
        
        if "biopsy" not in self.same_specimen_type:
            self.same_specimen_type.append("biopsy")
        if "excision" not in self.same_specimen_type:
            self.same_specimen_type.append("excision")
        if "resection" not in self.same_specimen_type:
            self.same_specimen_type.append("resection")
        
        self.same_specimen_type[1:] = sorted(self.same_specimen_type[1:])    
        return self.same_specimen_type
    
    def specimen_name_to_organ_and_procedure(self, specimen_name):
        
        self.specimen_organ_and_procedure = []
        
        try:
            specimen_info_list = self.specimen_dict[specimen_name]
        except:
            print(f"ERROR in specimen_name_to_organ_and_procedure: Specimen name ({specimen_name}) not found in the specimen list.")
            self.specimen_organ_and_procedure = ["***", "***"]  
            return self.specimen_organ_and_procedure
        
        self.specimen_organ_and_procedure = specimen_info_list[1], specimen_info_list[2]
        return  self.specimen_organ_and_procedure
    
    def print_organs(self):
        organ_list = []
        for key in self.specimen_dict:
            organ = self.specimen_dict[key][1]
            if organ not in organ_list:
                organ_list.append(organ)
                print(organ)
        

class SignoutCleanup:
        
    def __init__(self, template_dict):
        self.template_dict = template_dict
        self.typo_dict = typo_dict
        self.acronym_dict = acronym_dict
        self.all_caps_list = all_caps_list
        self.all_lower_list = all_lower_list
        self.special_cap_dict = special_capitalization_dict
        self.synonym_dict = synonym_dict
        self.st = SpecimenTemplates()
    
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
                self.template_dict[key] = (self.template_dict[key][0], (" ").join(description_list))
                
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
                self.template_dict[key] = (self.template_dict[key][0], (" ").join(description_list))
    
    def handle_capitalization(self):
        uppercase_list = self.all_caps_list
        lowercase_list = self.all_lower_list
        for key in self.template_dict:
            description_list: list = []
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
                self.template_dict[key] = (self.template_dict[key][0], (" ").join(description_list))
        
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
                self.template_dict[key] = (self.template_dict[key][0], (" ").join(description_list))
    
    def special_cleanup(self):
        for key in self.template_dict:
            description = self.template_dict[key][1].lower()
            if "to r/o" in description:
                description = description.split("to r/o")
                self.template_dict[key] = self.template_dict[key][0], description[0]
            elif "r/o" in description:
                description = description.split("r/o")
                self.template_dict[key] = self.template_dict[key][0], description[0]
    
    def organ_specific_cleanup(self):
        for key in self.template_dict:
            specimen_name = self.template_dict[key][0].lower().strip()
            template = self.st.specimen_name_to_organ_and_procedure(specimen_name=specimen_name)
            organ = template[0].strip()
            if organ == "None":
                pass
            if organ == "Adenoids":
                pass
            if organ == "Soft Tissue":
                pass
            if organ == "Adrenal gland":
                pass
            if organ == "Ampulla":
                pass
            if organ == "Digit":
                pass
            if organ == "Extremity":
                pass
            if organ == "Anus":
                pass
            if organ == "Anastomosis":
                pass
            if organ == "Blood vessel":
                pass
            if organ == "Appendix":
                pass
            if organ == "Atrial Appendage":
                pass
            if organ == "Bone":
                pass
            if organ == "Skin":
                pass
            if organ == "Bladder":
                pass
            if organ == "Body fluid":
                pass
            if organ == "Brain":
                pass
            if organ == "Branchial cleft cyst":
                pass
            if organ == "Breast":
                description_list = []
                description = self.template_dict[key][1]
                description_words = description.split(" ")
                for word in description_words:
                    if word.lower() == "right" or word.lower() == "left":
                        description_list.insert(0, f"{word},")
                    else:
                        description_list.append(word)
                self.template_dict[key] = (self.template_dict[key][0], (" ").join(description_list))
                        
            if organ == "Bronchus":
                pass
            if organ == "Joint":
                pass
            if organ == "Carina":
                pass
            if organ == "Colon":
                pass
            if organ == "Cervix":
                pass
            if organ == "Clot":
                pass
            if organ == "Conjunctiva":
                pass
            if organ == "Cornea":
                pass
            if organ == "Cul-de-sac":
                pass
            if organ == "Other":
                pass
            if organ == "Oral Cavity":
                pass
            if organ == "Ovary":
                pass
            if organ == "Diaphragm":
                pass
            if organ == "Spine":
                pass
            if organ == "Pancreas":
                pass
            if organ == "Intestine":
                pass
            if organ == "Duodenum":
                pass
            if organ == "Ear":
                pass
            if organ == "Endocervix":
                pass
            if organ == "Fallopian Tube":
                pass
            if organ == "Endometrium":
                pass
            if organ == "Epidural Space":
                pass
            if organ == "Epiglottis":
                pass
            if organ == "Esophagus":
                pass
            if organ == "Eye":
                pass
            if organ == "Foreign body":
                pass
            if organ == "Foreskin":
                pass
            if organ == "Gallbladder":
                pass
            if organ == "Stomach":
                pass
            if organ == "Gastroesophageal Junction":
                pass
            if organ == "Heart":
                pass
            if organ == "Hemorrhoids":
                pass
            if organ == "Hernia Sac":
                pass
            if organ == "Hydrocele Sac":
                pass
            if organ == "Vaginal Opening":
                pass
            if organ == "Ileocecal Valve":
                pass
            if organ == "Ileum":
                pass
            if organ == "Kidney":
                pass
            if organ == "Labia":
                pass
            if organ == "Lacrimal Sac":
                pass
            if organ == "Larynx":
                pass
            if organ == "Lip":
                pass
            if organ == "Liver":
                pass
            if organ == "Lung":
                pass
            if organ == "Lymph Node":
                pass
            if organ == "Sinonasal Cavity":
                pass
            if organ == "Mediastinum":
                pass
            if organ == "Meninges":
                pass
            if organ == "Mesentery":
                pass
            if organ == "Muscle":
                pass
            if organ == "Nail":
                pass
            if organ == "Nasolacrimal Duct":
                pass
            if organ == "Nerve":
                pass
            if organ == "Omentum":
                pass
            if organ == "Orbital Cavity":
                pass
            if organ == "Ovary and Fallopian Tubes":
                pass
            if organ == "Parathyroid Gland":
                pass
            if organ == "Parotid Gland":
                pass
            if organ == "Penis":
                pass
            if organ == "Perianal Region":
                pass
            if organ == "Pericardium":
                pass
            if organ == "Perineum":
                pass
            if organ == "Peritoneum":
                pass
            if organ == "Pharynx":
                pass
            if organ == "Pituitary Gland":
                pass
            if organ == "Placenta":
                pass
            if organ == "Pleura":
                pass
            if organ == "Products of Conception":
                pass
            if organ == "Prostate":
                pass
            if organ == "Prostate and Bladder":
                pass
            if organ == "Rectum":
                pass
            if organ == "Retroperitoneum":
                pass
            if organ == "Salivary Gland":
                pass
            if organ == "Scrotum":
                pass
            if organ == "Seminal Vesicle":
                pass
            if organ == "Septum":
                pass
            if organ == "Serosa":
                pass
            if organ == "Sinus Contents":
                pass
            if organ == "Small Bowel":
                pass
            if organ == "Spermatocele":
                pass
            if organ == "Spleen":
                pass
            if organ == "Stoma":
                pass
            if organ == "Synovium":
                pass
            if organ == "Tooth":
                pass
            if organ == "Tendon":
                pass
            if organ == "Testis":
                pass
            if organ == "Thymus":
                pass
            if organ == "Thyroid Gland":
                pass
            if organ == "Tongue":
                pass
            if organ == "Tonsil":
                pass
            if organ == "Trachea":
                pass
            if organ == "Umbilical Cord":
                pass
            if organ == "Ureter":
                pass
            if organ == "Urethra":
                pass
            if organ == "Uterus":
                pass
            if organ == "Uvula":
                pass
            if organ == "Vagina":
                pass
            if organ == "Spermatic Cord":
                pass
            if organ == "Vas Deferens":
                pass
            if organ == "Vocal Cord":
                pass
            if organ == "Vulva":
                pass
            if organ == "Pancreas, Duodenum, and Stomach":
                pass
    
    def remove_duplicate_word(self, to_keep, to_clean):
        rtn= [x for x in to_clean if x not in to_keep]
        return rtn

    def keep_duplicate_word(self, list1, list2):
        rtn= [x for x in list1 if x in list2]
        return rtn
   
    def remove_duplicate_words(self):
        for key in self.template_dict:
            specimen_name = self.template_dict[key][0].lower()
            template = self.st.specimen_name_to_organ_and_procedure(specimen_name=specimen_name)
        
            organ = template[0].lower().strip()
            if organ == "none": organ = None
            if organ == "other": organ = "***"
            organ_words = list(organ.split(" "))
            organ_words = organ_words + self.synonym_dict[organ]
            
            description = self.template_dict[key][1].lower().strip()
            description_words = list(description.split(" "))
            
            procedure = template[1].lower().strip()
            if procedure == "none": procedure = None
            if procedure == "other": procedure = "***"
            procedure_words = list(procedure.split(" "))
            
            
            
            cleaned_description1 = self.remove_duplicate_word(organ_words, description_words)
            cleaned_description2 = self.remove_duplicate_word(procedure_words, description_words)
            cleaned_description3 = self.keep_duplicate_word(cleaned_description1, cleaned_description2)
            
            self.template_dict[key] = (self.template_dict[key][0], (" ").join(cleaned_description3))
        return self.template_dict  
    
    def strip_description(self):
        for key in self.template_dict:
            self.template_dict[key] = (self.template_dict[key][0], self.template_dict[key][1].strip(",").strip().strip("'").strip('"'))
    
    def initial_cleanup(self):
        self.fix_typos()
        self.expand_acronyms()
        self.strip_description()
        self.special_cleanup()
        self.strip_description()
        self.organ_specific_cleanup()
        self.strip_description()
        self.remove_duplicate_words()
        return self.template_dict

    def final_cleanup(self):
        self.strip_description()
        self.handle_capitalization()
        self.special_capitalization()
        return self.template_dict

    def build_signout_template(self):
        self.return_dict: dict = {}
        self.initial_cleanup()
        self.final_cleanup()
        for key in self.template_dict:
            specimen_name = self.template_dict[key][0].strip()
            template = self.st.specimen_name_to_organ_and_procedure(specimen_name=specimen_name.lower())
            
            organ = template[0].strip()
            description = self.template_dict[key][1].strip()
            procedure = template[1].strip()
            
            if description:
                self.return_dict[key] = (f"{organ.title()}, {description}, {procedure.title()}:")
            else:
                self.return_dict[key] = (f"{organ.title()}, {procedure.title()}:")
            
            
        return self.return_dict
            
def main():

    test_dict = {'A': ['Breast mastectomy', "mass in right breast stitch at 12 o'clcok clcok NME"], 'B': ['Gastric biopsies', 'Rt stomach, r/o h. pylori'], 'C': ['leep', 'leep stitch at 12 clock'], 'D': ['Breast mastectomy', "12 CM breast lesion"]}
    st = SpecimenTemplates()
    sc = SignoutCleanup(template_dict=test_dict)
    #print(sc.build_signout_template())
    st.print_organs()

if __name__ == "__main__":
    main()
import textwrap
import code_diff as cd
from lib.AST_parser import ASTParser
from lib.AST_normalizer import ASTNormalizer
from lib.AST_comparator import ASTComparator
from lib.utils import Utils

if __name__ == "__main__":
    student_code = textwrap.dedent('''
    """Phone inventory."""
    
    
    def list_of_phones(all_phones: str) -> list:
        """
        Return list of phones.
    
        The input string contains of phone brands and models, separated by comma.
        Both the brand and the model do not contain spaces (both are one word).
        """
        if len(all_phones) == 0:
            return []
    
        return all_phones.split(",")
    
    
    def phone_brands(all_phones: str) -> list:
        """
        Return list of unique phone brands.
    
        The order of the elements should be the same as in the input string (first appearance).
        """
        phones = list_of_phones(all_phones)
        brands = []
    
        if len(all_phones) == 0:
            return []
    
        for i in phones:
            i = i.split(" ")
    
            if i[0] in brands:
                continue
            
            brands.append(i[0])
    
        return brands
    
    
    def phone_models(all_phones: str) -> list:
        """
        Return list of unique phone models.
    
        The order of the elements should be the same as in the input string (first appearance).
        """
        phones = list_of_phones(all_phones)
        brands = phone_brands(all_phones)
        models = []
    
        if len(all_phones) == 0:
            return []
    
        for i in phones:
            i = i.split(" ")
    
            for e in brands:
                if i[0] == e:
                    i.pop(0)
    
            i = " ".join(i)
            if i in models:
                continue
            
            models.append(i)
    
        return models
    
    
    def search_by_brand(all_phones: str, brand: str) -> list:
        """
        Search for phones by brand.
    
        The search is case-insensitive.
        """
        phones = list_of_phones(all_phones)
        results = []
    
        for i in phones:
            i = i.split(" ")
            for x in i:
            
                if brand.lower().count(x.lower()) > 0:
                    results.append(" ".join(i))
                    break
                
        return results
    
    
    def search_by_model(all_phones: str, model: str) -> list:
        """
        Search for phones by model.
    
        The search is case-insensitive.
        """
        phones = list_of_phones(all_phones)
        brands = phone_brands(all_phones)
        results = []
    
        if model in brands:
            return []
    
        for x in phones:
            i = x.lower().split(" ")
    
            if model.lower() in i:
                results.append(x)
    
        return results
    ''')

    teacher_code = textwrap.dedent('''
    """Phone inventory."""


    def list_of_phones(all_phones: str) -> list:
        """
        Return list of phones.

        The input string contains of phone brands and models, separated by comma.
        Both the brand and the model do not contain spaces (both are one word).
        """
        if len(all_phones) == 0:
            return []
        else:
            phones = all_phones.split(",")
        return phones


    def phone_brands(all_phones: str) -> list:
        """
        Return list of unique phone brands.

        The order of the elements should be the same as in the input string (first appearance).
        """
        brands = []
        phones = all_phones.split(",")
        if len(all_phones) == 0:
            return []
        else:
            for phone in phones:
                brand = phone.partition(" ")[0]
                if brand not in brands:
                    brands.append(brand)
        return brands


    def phone_models(all_phones: str) -> list:
        """
        Return list of unique phone models.

        The order of the elements should be the same as in the input string (first appearance).
        """
        models = []
        phones = all_phones.split(",")
        if len(all_phones) == 0:
            return []
        for phone in phones:
            model = phone.partition(" ")[2]
            if model not in models:
                models.append(model)
        return models


    def search_by_brand(all_phones: str, brand: str) -> list:
        """
        Search for phones by brand.

        The search is case-insensitive.
        """
        phones = all_phones.split(",")
        search_result = []
        if len(all_phones) == 0:
            return []
        for phone in phones:
            phone_without_spaces = phone.strip()
            brand_in_phone = phone_without_spaces.split()[0]
            if brand_in_phone.lower() == brand.lower():
                search_result.append(phone_without_spaces)
        return search_result


    def search_by_model(all_phones: str, model: str) -> list:
        """
        Search for phones by model.

        The search is case-insensitive.
        """
        if len(model) == 0 or len(all_phones) == 0:
            return []
        phones = all_phones.split(",")
        search_result = []

        for phone in phones:
            phone_without_spaces = phone.strip()
            model_parts = phone_without_spaces.split()[1:]
            for model_part in model_parts:
                if model.lower() == model_part.lower():
                    search_result.append(phone_without_spaces)
                    break
        return search_result
    ''')


    utils = Utils()
    
    student_funcs_dict = utils.extract_functions(student_code)
    teacher_funcs_dict = utils.extract_functions(teacher_code)

    differences = utils.compare(student_funcs_dict, teacher_funcs_dict)

    print(differences)

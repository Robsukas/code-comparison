import copy
import builtins


class ASTNormalizer:
    def normalize_ast_dict(self, ast_dict, name_map=None, counter_start=1):
        if name_map is None:
            name_map = {}
        current_counter = counter_start

        if not isinstance(ast_dict, dict) or '_type' not in ast_dict:
            return ast_dict, name_map, current_counter

        new_dict = copy.deepcopy(ast_dict)
        node_type = new_dict['_type']

        if node_type == 'Name':
            old_name = new_dict['id']

            if old_name not in dir(builtins):
                if old_name not in name_map:
                    new_name = f"a{current_counter}"
                    name_map[old_name] = new_name
                    current_counter += 1
                new_dict['id'] = name_map[old_name]

        elif node_type == 'arg':
            old_name = new_dict['arg']

            if old_name not in dir(builtins):
                if old_name not in name_map:
                    new_name = f"a{current_counter}"
                    name_map[old_name] = new_name
                    current_counter += 1
                new_dict['arg'] = name_map[old_name]

        elif node_type == 'FunctionDef':
            old_name = new_dict['name']

            if old_name not in dir(builtins):
                if old_name not in name_map:
                    new_name = f"a{current_counter}"
                    name_map[old_name] = new_name
                    current_counter += 1
                new_dict['name'] = name_map[old_name]

        for key, value in new_dict.items():
            if key == '_type':
                continue

            if isinstance(value, dict):
                child_dict, name_map, current_counter = self.normalize_ast_dict(value, name_map, current_counter)
                new_dict[key] = child_dict

            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        norm_item, name_map, current_counter = self.normalize_ast_dict(item, name_map, current_counter)
                        new_list.append(norm_item)
                    else:
                        new_list.append(item)
                new_dict[key] = new_list

        return new_dict, name_map, current_counter

class ASTComparator:
    def compare_ast_dicts(self, dict_a, dict_b, path=""):
        differences = []

        # check if is leaf node, if yes, compare both dicts directly for possible mismatch
        if not (isinstance(dict_a, dict) and '_type' in dict_a):
            if dict_a != dict_b:
                differences.append(f"{path}: Value mismatch => {dict_a} != {dict_b}")
            return differences

        # check if is leaf node, if yes, compare both dicts directly for possible mismatch
        if not (isinstance(dict_b, dict) and '_type' in dict_b):
            if dict_a != dict_b:
                differences.append(f"{path}: Value mismatch => {dict_a} != {dict_b}")
            return differences

        # check for node type mismatch
        if dict_a['_type'] != dict_b['_type']:
            differences.append(f"{path}: Node type mismatch => {dict_a['_type']} vs {dict_b['_type']}")
            return differences

        node_type = dict_a['_type']

        # unionize all keys from both dicts into one set
        all_keys = set(dict_a.keys()) | set(dict_b.keys())

        for key in all_keys:
            if key == '_type':
                continue

            # rebuild path
            new_path = f"{path}/{node_type}.{key}" if path else f"{node_type}.{key}"
            val_a = dict_a.get(key)
            val_b = dict_b.get(key)

            # check for missing keys
            if key not in dict_a:
                differences.append(f"{new_path}: Missing in first dict")
                continue
            if key not in dict_b:
                differences.append(f"{new_path}: Missing in second dict")
                continue

            # compare recursively if lists
            if isinstance(val_a, list) and isinstance(val_b, list):
                if len(val_a) != len(val_b):
                    differences.append(f"{new_path}: List length mismatch => {len(val_a)} vs {len(val_b)}")
                    continue
                for i, (sub_a, sub_b) in enumerate(zip(val_a, val_b)):
                    sub_path = f"{new_path}[{i}]"
                    differences.extend(self.compare_ast_dicts(sub_a, sub_b, path=sub_path))
            else:
                differences.extend(self.compare_ast_dicts(val_a, val_b, path=new_path))

        return differences

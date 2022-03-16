import json
import re

import pymorphy2


class BooleanSearch:
    def __init__(self, index_path):
        self.operands_functions = {
            "&": lambda x, y: list(set(x) & set(y)),
            "|": lambda x, y: x + y
        }
        self.operands_functions_priority = {
            "&": 1,
            "|": 2
        }
        self.operands = ("(", ")", "&", "|")
        self.morph = pymorphy2.MorphAnalyzer()
        self.indexes = dict()
        self.read_indexes_file(index_path)

    def read_indexes_file(self, path):
        try:
            file = open(path, "r", encoding="utf-8")
            lines = file.readlines()
            self.indexes = json.loads(lines[0])
        except Exception:
            print("Cant read indexes file")

    def get_or_default(self, word):
        p = self.morph.parse(word)[0]
        if p.normalized.is_known:
            normal_form = p.normal_form
        else:
            normal_form = word.lower()
        if normal_form in self.indexes:
            return self.indexes[normal_form]
        else:
            return set()

    def search(self, query):
        parsed_query = []
        result_query = []
        parsed_query_words = []
        query_parts = re.split("\\s+", query)
        last_operation = None
        for part in query_parts:
            if part[0] == "(":
                if last_operation is not None and last_operation not in self.operands:
                    result_query.append("&")
                    parsed_query.append("&")
                result_query.append("(")
                result_query.append(self.get_or_default(part[1:]))
                parsed_query.append("(")
                parsed_query.append(part[1:])
                parsed_query_words.append(part[1:])
            elif part[-1] == ")":
                if last_operation is not None and last_operation not in self.operands:
                    result_query.append("&")
                    parsed_query.append("&")
                result_query.append(self.get_or_default(part[:-1]))
                result_query.append(")")

                parsed_query.append(part[:-1])
                parsed_query.append(")")

                parsed_query_words.append(part[:-1])
            elif part in self.operands:
                result_query.append(part)
                parsed_query.append(part)
            else:
                if (last_operation is not None and last_operation not in self.operands) or (
                        last_operation is not None and last_operation == ")"):
                    result_query.append("&")
                    result_query.append(self.get_or_default(part))

                    parsed_query.append("&")
                    parsed_query.append(part)

                    parsed_query_words.append(part)
                else:
                    result_query.append(self.get_or_default(part))
                    parsed_query.append(part)
                    parsed_query_words.append(part)
            last_operation = part
        print(f"Parsed query: {parsed_query}")
        return self.compute_query(result_query, self.operands_functions, {},
                                  self.operands_functions_priority), parsed_query, parsed_query_words

    def compute_query(self, query, operands_functions, unary_operator, operands_functions_priority):
        operation_stack = []
        value_stack = []
        for query_operation in query:
            if query_operation == "(":
                operation_stack.append(query_operation)
            elif query_operation == ")":
                # compute all until open bracket
                is_operation_stack_empty = len(operation_stack) == 0
                while not is_operation_stack_empty and operation_stack[-1] != "(":
                    last = operation_stack[-1]
                    if last in operands_functions.keys():
                        # get last two value
                        x = value_stack[-2]
                        y = value_stack[-1]
                        value_stack = value_stack[:-2]
                        value_stack.append(operands_functions[last](x, y))
                    else:
                        x = value_stack[-1]
                        value_stack.pop()
                        value_stack.append(unary_operator[last](x))
                    operation_stack.pop()
                if len(operation_stack) == 0:
                    print(f"Brackets error in query: {query}")
                    return None
                operation_stack.pop()
            elif type(query_operation) is str and (
                    query_operation in unary_operator.keys() or query_operation in operands_functions.keys()):
                while len(operation_stack) != 0 and operation_stack[-1] != "(" and operands_functions_priority[
                    operation_stack[-1]] > operands_functions_priority[query_operation]:
                    last = operation_stack[-1]
                    if last in operands_functions.keys():
                        # get last two value
                        x = value_stack[-2]
                        y = value_stack[-1]
                        value_stack = value_stack[:-2]
                        value_stack.append(operands_functions[last](x, y))
                    else:
                        x = value_stack[-1]
                        value_stack.pop()
                        value_stack.append(unary_operator[last](x))
                    operation_stack.pop()
                operation_stack.append(query_operation)
            else:
                value_stack.append(query_operation)

        while len(operation_stack) != 0:
            last = operation_stack[-1]
            if last in operands_functions.keys():
                x = value_stack[-2]
                y = value_stack[-1]
                value_stack = value_stack[:-2]
                value_stack.append(operands_functions[last](x, y))
            else:
                x = value_stack[-1]
                value_stack.pop()
                value_stack.append(unary_operator[last](x))
            operation_stack.pop()

        if len(value_stack) != 1:
            print(f"Cant parse query: {query}")

        return value_stack[0]


query = "(main Microsoft browser security store)"
indexes_path = "./index.json"
print(f"Your query: '{query}'")
booleanSearch = BooleanSearch(indexes_path)
result_documents, _, found_word = booleanSearch.search(query)
print(result_documents)
print(found_word)

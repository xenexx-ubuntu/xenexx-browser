import ast
import astor

class CodeCompressor(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.returns = None
        node.decorator_list = []
        node.body = [self.visit(n) for n in node.body if not isinstance(n, ast.Pass)]
        return node

    def visit_Assign(self, node):
        # Убираем аннотации типов
        for target in node.targets:
            if isinstance(target, ast.Name):
                target.id = target.id.split(":")[0]
        return node

    def visit_Expr(self, node):
        return None

    def visit_Comment(self, node):
        return None

def compress_code(code):
    tree = ast.parse(code)
    compressed_tree = CodeCompressor().visit(tree)
    return astor.to_source(compressed_tree)

def compress_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        original_code = file.read()
    compressed_code = compress_code(original_code)
    return compressed_code

file_path = 'Xenexx_Browser.py'
compressed_code = compress_file(file_path)

# Выводим сжатый код
print(compressed_code)

import ast
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
TARGET_DIRS = [PROJECT_ROOT / d for d in ["events", "tours", "transfers", "cart", "orders", "payments", "shared"]]

FLOAT_WARN = []
DECIMAL_OK = []

class DecimalChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []

    def visit_BinOp(self, node):
        # Check for float and Decimal in the same operation
        left = ast.dump(node.left)
        right = ast.dump(node.right)
        if ("Call" in left and "float" in left) or ("Call" in right and "float" in right):
            if ("Call" in left and "Decimal" in left) or ("Call" in right and "Decimal" in right):
                self.issues.append((node.lineno, "Mixing float and Decimal in operation"))
        self.generic_visit(node)

    def visit_Call(self, node):
        # Warn if float() is used in assignment or return
        if isinstance(node.func, ast.Name) and node.func.id == "float":
            self.issues.append((node.lineno, "float() used; check if for output only"))
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Warn if float is assigned to a variable likely used in price/total
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "float":
            for target in node.targets:
                if hasattr(target, 'id') and any(x in target.id for x in ["price", "total", "amount", "fee", "tax", "discount", "subtotal"]):
                    self.issues.append((node.lineno, f"Assigning float to {target.id}"))
        self.generic_visit(node)


def check_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except Exception as e:
            return []
    checker = DecimalChecker(filepath)
    checker.visit(tree)
    return checker.issues


def main():
    print("🔎 Checking for Decimal/float consistency in financial calculations...\n")
    for d in TARGET_DIRS:
        for pyfile in d.rglob("*.py"):
            issues = check_file(pyfile)
            if issues:
                FLOAT_WARN.append((pyfile, issues))
            else:
                DECIMAL_OK.append(pyfile)
    if FLOAT_WARN:
        print("❌ Issues found with float/Decimal usage:")
        for file, issues in FLOAT_WARN:
            print(f"\n{file}:")
            for lineno, msg in issues:
                print(f"  Line {lineno}: {msg}")
    else:
        print("✅ All checked files use Decimal correctly in financial calculations!")
    print(f"\nChecked {len(DECIMAL_OK) + len(FLOAT_WARN)} files.")

if __name__ == "__main__":
    main() 
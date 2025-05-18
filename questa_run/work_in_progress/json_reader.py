import json


try:
    with open('data.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("The file was not found")
except json.JSONDecodeError:
    print("The file contains invalid JSON")
    
    
    with open("output.json", "w") as file:
    json.dump(data, file)  # Serialize and write to file
    
    
class ASTNode:
    def __init__(self, tag, text=None, children=None, start=None, end=None):
        self.tag = tag
        self.text = text
        self.children = children or []
        self.start = start
        self.end = end

    def __repr__(self):
        return f"ASTNode(tag={self.tag}, text={self.text}, children={len(self.children)})"
    
def walk(node):
    print(f"Node: {node['tag']} (text: {node.get('text')})")
    for child in node.get("children", []):
        walk(child)

walk(ast)  # Start from root
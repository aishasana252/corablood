import sys
from html.parser import HTMLParser

class Balanced(HTMLParser): 
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.tags_to_track = ['div', 'template', 'section', 'main', 'table', 'tbody', 'tr']

    def handle_starttag(self, tag, attrs): 
        if tag in self.tags_to_track:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.tags_to_track:
            if not self.stack:
                self.errors.append(f"Extra close {tag} at {self.getpos()}")
            else:
                last, pos = self.stack.pop()
                if last != tag:
                    self.errors.append(f"Mismatched {tag} at {self.getpos()}, expected {last} from {pos}")

def check_file(filename):
    p = Balanced()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            p.feed(f.read())
        print(f"Unclosed tags: {len(p.stack)}")
        for tag, pos in p.stack:
            print(f"  {tag} opened at line {pos[0]} col {pos[1]}")
        print(f"Errors: {len(p.errors)}")
        for err in p.errors:
            print(f"  {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_file('d:/CoraBlood-Ultimat-main/templates/donors/workflow.html')

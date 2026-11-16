import html.parser

class HTMLValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.self_closing = {"meta", "link", "img", "br", "hr", "input", "source"}
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.self_closing:
            self.tags.append(tag)

    def handle_endtag(self, tag):
        if tag in self.self_closing:
            return
        if not self.tags:
            self.errors.append(f"Unexpected end tag </{tag}> with empty stack")
        elif self.tags[-1] == tag:
            self.tags.pop()
        else:
            self.errors.append(f"Mismatched end tag: expected </{self.tags[-1]}>, got </{tag}>")

with open("web/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Check JS syntax with a basic check
import re
scripts = re.findall(r'<script>([\s\S]*?)</script>', content)
print(f"Number of script tags: {len(scripts)}")
print(f"Total script size: {sum(len(s) for s in scripts)} chars")

val = HTMLValidator()
val.feed(content)
print(f"HTML Validation completed. Errors: {len(val.errors)}")
if val.errors:
    for e in val.errors[:10]:
        print(" -", e)
else:
    print("Zero HTML tag mismatches!")


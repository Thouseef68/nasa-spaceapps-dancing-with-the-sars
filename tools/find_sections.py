with open("web/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, l in enumerate(lines):
    if "<script" in l or "</script" in l:
        print(f"Line {i+1}: {l.strip()}")
    if "<body" in l or "</body" in l:
        print(f"Line {i+1}: {l.strip()}")


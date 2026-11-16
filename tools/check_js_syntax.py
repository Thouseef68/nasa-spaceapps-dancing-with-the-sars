import re
import subprocess

with open("web/index.html", "r", encoding="utf-8") as f:
    text = f.read()

scripts = re.findall(r'<script>([\s\S]*?)</script>', text)
assert len(scripts) == 1

js_code = scripts[0]
with open("tools/temp_check.js", "w", encoding="utf-8") as f:
    f.write(js_code)

res = subprocess.run(["node", "--check", "tools/temp_check.js"], capture_output=True, text=True)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)
if res.returncode == 0:
    print("JS syntax is 100% valid and verified!")


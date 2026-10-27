"""Helpers for book tables transcribed from frozen evaluation sources."""
import csv, json, re

def export(folder, rows):
    assert rows and all(r.get("source") for r in rows)
    with (folder/"data.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def table(folder, headers, rows, caption):
    lines=["| "+" | ".join(headers)+" |", "| "+" | ".join(["---"]*len(headers))+" |"]
    assert all(len(row)==len(headers) for row in rows)
    lines.extend("| "+" | ".join(map(str,row))+" |" for row in rows)
    (folder/"output.md").write_text("\n".join(lines)+"\n\n: "+caption+"\n",encoding="utf-8")

def latex_rows(path):
    result=[]
    for line in path.read_text().splitlines():
        if not (re.search(r"&\s*[a-z]{3}\s*&",line) or ("&" in line and ("Average" in line or "Avg (" in line))):
            continue
        line=line.strip().removesuffix(r"\\").strip()
        line=re.sub(r"\\textbf\{([^{}]+)\}",r"\1",line)
        line=line.replace(r"$^\ddagger$","^‡^").replace(r"$^\dagger$","^†^")
        result.append([v.strip() for v in line.split("&")])
    return result

def paired(values, offset):
    out=[]
    for i,v in enumerate(values):
        other=values[(i+offset)%(2*offset)]
        if v=="---": out.append("—"); continue
        assert 0<=float(v)<=100
        out.append("**"+v+"**" if other!="---" and float(v)>float(other) else v)
    return out

"""Rebuilds timeline.html from scripts/tasks.json. Run: python3 scripts/build_timeline.py"""
import json,pathlib
r=pathlib.Path(__file__).parent
t=(r/"timeline.template.html").read_text().replace("__TASKS__",json.dumps(json.load(open(r/"tasks.json")),ensure_ascii=False))
(r.parent/"timeline.html").write_text(t)

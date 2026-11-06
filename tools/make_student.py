#!/usr/bin/env python3
"""Generate a student notebook from a solution notebook.

The solution notebook is the single source of truth. Cells are marked with tags
(JupyterLab: right sidebar -> "Common Tools" -> cell tags):

  answer          markdown answer box; the student version keeps only the empty box
  solution        code cell; the student version is metadata["student_source"]
  solution-only   cell is removed from the student version

All outputs and execution counts are stripped.

usage:
  python3 tools/make_student.py notebooks/exercise03/Exercise03_Solutions.ipynb notebooks/exercise03/Exercise03.ipynb
"""
import json
import sys

EMPTY_ANSWER = '<div class="alert alert-success">\n\n*--> (put your text here)*\n\n</div>'


def lines(s):
    ls = s.split("\n")
    return [l + "\n" for l in ls[:-1]] + [ls[-1]]


def make_student(solution_path, student_path):
    nb = json.load(open(solution_path, encoding="utf-8"))
    cells = []
    for cell in nb["cells"]:
        tags = cell.get("metadata", {}).get("tags", [])
        if "solution-only" in tags:
            continue
        cell = json.loads(json.dumps(cell))  # deep copy
        if "answer" in tags:
            cell["source"] = lines(EMPTY_ANSWER)
        if "solution" in tags:
            if "student_source" not in cell["metadata"]:
                raise ValueError(f"cell {cell.get('id')} is tagged 'solution' but has no metadata['student_source']")
            cell["source"] = lines(cell["metadata"]["student_source"])
        cell["metadata"] = {}
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        cells.append(cell)
    nb["cells"] = cells
    with open(student_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(nb, ensure_ascii=False))
    n_removed = len(json.load(open(solution_path, encoding="utf-8"))["cells"]) - len(cells)
    print(f"{student_path}: {len(cells)} cells ({n_removed} solution-only cells removed)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    make_student(sys.argv[1], sys.argv[2])

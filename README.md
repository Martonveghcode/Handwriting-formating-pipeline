
# Handwriting-formating-pipeline

An extension/pipeline to **“My Text in Your Handwriting”** by Thaines. Includes text formatting, limited Unicode→ASCII support, a print-formatting pipeline, and training-data processing macros/utils — plus a recommended training sheet.

> **Note:** This is **not** a full installation guide for the original project. For setup, see:
> [My Text in Your Handwriting (HELIT)](https://github.com/thaines/helit/tree/master/handwriting#my-text-in-your-handwriting)

---

## Quick tips (what worked for me)

1. **Ubuntu 20.04.6 LTS (WSL2)** — newer Ubuntu versions gave me issues with GTK/Python2 and inline C compilation.
2. **Python 2.7** runtime with:

   * `python-gi`, `gir1.2-gtk-3.0` (GTK bindings)
   * `python-cairo`
   * `python2-dev` / `python-dev`, `build-essential`
   * `numpy==1.16.6`, `scipy==0.19.1` (provides `scipy.weave`)
3. If you hit missing imports (`gi`, `cairo`, `weave`), install the packages above and re-run.
4. Use system Python 2 (not a Python 3 venv) for the **LET/HST** tools.

---

## Build notes & fixes

### Symptom

Running `python2 main.py` in `helit/handwriting/let` failed with:

```
ImportError: .../line_graph_c.so: undefined symbol: HalfToEdge
```

### Cause

`HalfToEdge` was defined **twice**:

* Correct, **inline** definition in
  `helit/handwriting/let/line_graph/line_graph_c.h`
* A **duplicate/conflicting** definition left in
  `helit/handwriting/let/line_graph/line_graph_c.c` (≈ line **5935**)

This duplicate caused compile/link/runtime symbol issues.

### Fix (single source change)

**Remove** the duplicate from `line_graph_c.c` and rely on the header’s inline version.

**Before** (❌ in `.c`, around ~5935):

```c
// line_graph_c.c — this should NOT exist here
Edge * HalfToEdge(HalfEdge * half) {
    return half ? half->edge : NULL;
}
```

**After** (✅ keep only in `.h`):

```c
// line_graph_c.h — canonical definition
inline Edge * HalfToEdge(HalfEdge * half)
{
    if (half->reverse < half) half = half->reverse;
    return (Edge*)(void*)((char*)(void*)half - offsetof(Edge, pos));
}
```

### Result

* `LET` (Line Extraction & Tagging) launches and runs on **Ubuntu 20.04.6 LTS** with **Python 2.7**.
* No other source edits were needed beyond removing the duplicate function.

---





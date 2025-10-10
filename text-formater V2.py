import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

DEFAULT_REPLACEMENTS = [
    ("\\u00e1", "#"),
    ("\\u00e9", "$"),
    ("\\u00ed", "["),
    ("\\u00f3", "^"),
    ("\\u00fa", "`"),
    ("\\u00e0", "~"),
    ("\\u00e8", "]"),
    ("\\u00f2", "}"),
    ("\\u00fc", "{"),
    ("\\u00ef", "|"),
    ("\\u00f1", "*"),
    ("\\u00e7", "@"),
    ("\"", "\""),
    ("(", "("),
    (")", ")"),
    ("!", "!"),
    ("%", "%"),
    ("?", "?"),
    ("-", "-"),
    (":", ":"),
    (";", ";"),
    ("/", "/"),
    ("'", "'"),
]


def decode_symbol(symbol: str) -> str:
    try:
        return bytes(symbol, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return symbol

REPLACEMENT_KEYS = [(decode_symbol(original), default) for original, default in DEFAULT_REPLACEMENTS]

PARAGRAPH_SPACER = "<            <"
PAGE_BREAK_LINE = "---------------"


def split_into_paragraphs(text: str):
    paragraphs = []
    current_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            current_lines.append(line)
        else:
            if current_lines:
                paragraphs.append(" ".join(current_lines))
                current_lines = []
    if current_lines:
        paragraphs.append(" ".join(current_lines))

    if not paragraphs and text.strip():
        paragraphs.append(text.strip())

    return paragraphs


def format_paragraph(words, min_words=7, max_words=10, target_width=54, tolerance=4):
    lines = []
    i = 0
    n = len(words)

    while i < n:
        best_line = None
        best_diff = float("inf")

        for count in range(max_words, min_words - 1, -1):
            if i + count > n:
                continue
            segment = words[i : i + count]
            joined = " ".join(segment)
            length = len(joined)

            diff = abs(length - target_width)

            if length <= target_width + tolerance and diff < best_diff:
                best_line = segment
                best_diff = diff

        if best_line:
            line = " ".join(best_line)
            lines.append(f"< {line} <")
            i += len(best_line)
        else:
            temp_line = []
            total_len = 0
            while i < n and len(temp_line) < max_words:
                word_len = len(words[i]) + (1 if temp_line else 0)
                if total_len + word_len > target_width + tolerance:
                    break
                total_len += word_len
                temp_line.append(words[i])
                i += 1
            if temp_line:
                lines.append(f"< {' '.join(temp_line)} <")
            else:
                lines.append(f"< {words[i]} <")
                i += 1
    return lines


def format_text(input_text, min_words=7, max_words=10, target_width=54, tolerance=4, lines_per_page=33):
    paragraphs = split_into_paragraphs(input_text)

    if not paragraphs:
        return PARAGRAPH_SPACER, False

    formatted_lines = []
    page_line_count = 0
    effective_limit = max(0, int(lines_per_page)) if lines_per_page is not None else 0

    for idx, paragraph_text in enumerate(paragraphs):
        words = paragraph_text.split()
        if not words:
            continue

        paragraph_lines = format_paragraph(
            words,
            min_words=min_words,
            max_words=max_words,
            target_width=target_width,
            tolerance=tolerance,
        )

        for line in paragraph_lines:
            if effective_limit and page_line_count == effective_limit:
                formatted_lines.append(PAGE_BREAK_LINE)
                page_line_count = 0
            formatted_lines.append(line)
            if effective_limit:
                page_line_count += 1

        has_next_paragraph = idx < len(paragraphs) - 1
        if has_next_paragraph:
            if effective_limit and page_line_count == effective_limit:
                formatted_lines.append(PAGE_BREAK_LINE)
                page_line_count = 0
            else:
                formatted_lines.append(PARAGRAPH_SPACER)
                if effective_limit:
                    page_line_count += 1
                    if page_line_count == effective_limit:
                        formatted_lines.append(PAGE_BREAK_LINE)
                        page_line_count = 0

    if not formatted_lines or formatted_lines[-1] != PARAGRAPH_SPACER:
        if effective_limit and page_line_count == effective_limit:
            formatted_lines.append(PAGE_BREAK_LINE)
        formatted_lines.append(PARAGRAPH_SPACER)

    return "\n".join(formatted_lines), False


def apply_replacements(text, mapping):
    result = text
    for original, replacement in mapping.items():
        result = result.replace(original, replacement)
    return result


def build_replacement_mapping():
    mapping = {}
    for original, default in REPLACEMENT_KEYS:
        value = replacement_vars[original].get().strip()
        if not value:
            value = default
        mapping[original] = value[0]
    return mapping


def on_format():
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:
        status_var.set("Nothing to format")
        return

    line_limit_value = line_limit_var.get().strip()
    line_limit_warning = False
    try:
        lines_per_page = int(line_limit_value)
    except ValueError:
        lines_per_page = 33
        line_limit_warning = True
    if lines_per_page < 0:
        lines_per_page = 0
        line_limit_warning = True
    if line_limit_warning:
        line_limit_var.set(str(lines_per_page))

    mapping = build_replacement_mapping()
    processed_text = apply_replacements(input_text, mapping)
    formatted, oversized_paragraph = format_text(processed_text, lines_per_page=lines_per_page)

    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, formatted)
    output_text.config(state="disabled")

    status_bits = ["Formatted text with replacement mapping"]
    if line_limit_warning:
        status_bits.append("(line limit invalid or negative; using adjusted value)")
    if oversized_paragraph:
        status_bits.append("(warning: a paragraph exceeds the page line limit)")
    status_var.set(" ".join(status_bits))


def copy_output():
    content = output_text.get("1.0", tk.END).strip()
    if not content:
        status_var.set("Nothing to copy")
        return
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update_idletasks()
    status_var.set("Output copied to clipboard")


root = tk.Tk()
root.title("Smart Text Block Formatter")
root.minsize(920, 700)
root.configure(bg="#f3f4f6")

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure("TFrame", background="#f3f4f6")
style.configure("Card.TFrame", background="#ffffff")
style.configure("Card.TLabelframe", background="#ffffff", borderwidth=0)
style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff")
style.map(
    "Accent.TButton",
    background=[("!disabled", "#2563eb"), ("active", "#3b82f6"), ("pressed", "#1d4ed8")],
    foreground=[("disabled", "#d1d5db"), ("!disabled", "#ffffff")],
)
style.configure("Secondary.TButton", font=("Segoe UI", 10))
style.map(
    "Secondary.TButton",
    background=[("!disabled", "#e5e7eb"), ("active", "#dbeafe"), ("pressed", "#d1d5db")]
)
style.configure("Status.TLabel", font=("Segoe UI", 10), background="#f3f4f6", foreground="#374151")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame = ttk.Frame(root, padding=(20, 20, 20, 20))
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure(0, weight=1)

header = ttk.Frame(main_frame, style="Card.TFrame", padding=(20, 15))
header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
header.columnconfigure(0, weight=1)

heading = ttk.Label(
    header,
    text="MyText Handwriting Formatter",
    font=("Segoe UI", 18, "bold"),
    background="#ffffff",
)
heading.grid(row=0, column=0, sticky="w")

subheading = ttk.Label(
    header,
    text="Format paragraphs for MyText handwriting exports and swap accented characters for ASCII placeholders.",
    background="#ffffff",
    foreground="#4b5563",
)
subheading.grid(row=1, column=0, sticky="w", pady=(6, 0))

content = ttk.Frame(main_frame)
content.grid(row=1, column=0, sticky="nsew")
content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=2)

mono_font = tkfont.Font(family="Courier", size=11)

input_section = ttk.LabelFrame(content, text="Input Text", padding=15, style="Card.TLabelframe")
input_section.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
input_section.columnconfigure(0, weight=1)

input_hint = ttk.Label(
    input_section,
    text="Paste or type text to be formatted. The formatter will insert angle brackets and balance line widths.",
    foreground="#4b5563",
)
input_hint.grid(row=0, column=0, sticky="w", pady=(0, 8))

text_input = tk.Text(input_section, height=12, wrap="word", font=mono_font, borderwidth=0, highlightthickness=1)
text_input.grid(row=1, column=0, sticky="nsew")
input_section.rowconfigure(1, weight=1)

replacement_section = ttk.LabelFrame(content, text="Character Replacement Chart", padding=15, style="Card.TLabelframe")
replacement_section.grid(row=0, column=1, sticky="nsew")
replacement_section.columnconfigure((0, 1, 2, 3), weight=1)

replacement_vars = {}
for idx, (original, default) in enumerate(REPLACEMENT_KEYS):
    row = idx // 2
    col = (idx % 2) * 2

    label = ttk.Label(replacement_section, text=f"{original} ->", foreground="#111827")
    label.grid(row=row, column=col, sticky="e", padx=(0, 6), pady=4)

    var = tk.StringVar(value=default)
    entry = ttk.Entry(replacement_section, textvariable=var, width=6, justify="center")
    entry.grid(row=row, column=col + 1, sticky="w", pady=4)
    replacement_vars[original] = var

buttons_frame = ttk.Frame(main_frame)
buttons_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
buttons_frame.columnconfigure(2, weight=1)

line_limit_var = tk.StringVar(value="33")

line_limit_label = ttk.Label(buttons_frame, text="Lines per Page:")
line_limit_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

line_limit_entry = ttk.Entry(buttons_frame, width=6, textvariable=line_limit_var, justify="center")
line_limit_entry.grid(row=0, column=1, sticky="w", padx=(0, 16))

format_button = ttk.Button(buttons_frame, text="Format Text", command=on_format, style="Accent.TButton")
format_button.grid(row=0, column=2, sticky="w")

output_section = ttk.LabelFrame(main_frame, text="Formatted Output", padding=15, style="Card.TLabelframe")
output_section.grid(row=3, column=0, sticky="nsew", pady=(15, 0))
output_section.columnconfigure(0, weight=1)
output_section.rowconfigure(0, weight=1)

output_text = tk.Text(output_section, height=16, wrap="none", font=mono_font, borderwidth=0, highlightthickness=1, state="disabled")
output_text.grid(row=0, column=0, sticky="nsew")

scroll_x = ttk.Scrollbar(output_section, orient="horizontal", command=output_text.xview)
scroll_x.grid(row=1, column=0, sticky="ew", pady=(10, 0))
output_text.configure(xscrollcommand=scroll_x.set)

copy_button = ttk.Button(output_section, text="Copy Output", command=copy_output, style="Secondary.TButton")
copy_button.grid(row=2, column=0, sticky="e", pady=(12, 0))

status_var = tk.StringVar(value="Ready")
status_label = ttk.Label(main_frame, textvariable=status_var, style="Status.TLabel")
status_label.grid(row=4, column=0, sticky="w", pady=(12, 0))

root.mainloop()

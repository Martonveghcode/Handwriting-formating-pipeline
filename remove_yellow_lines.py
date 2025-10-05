from gimpfu import *

def remove_yellow_lines(img, layer):
    pdb.gimp_image_undo_group_start(img)

    # Set a sample threshold for color similarity (adjust if needed)
    pdb.gimp_context_set_sample_threshold(0.2)

    # Yellow shades to remove:
    # Example 1: pale yellow (#FBEFB2) = RGB(251, 239, 178)
    pdb.gimp_image_select_color(img, CHANNEL_OP_REPLACE, layer, (251, 239, 178))

    # Example 2: saturated yellow (#F1E200) = RGB(241, 226, 0)
    pdb.gimp_image_select_color(img, CHANNEL_OP_ADD, layer, (241, 226, 0))

    # Fill selection with white
    pdb.gimp_context_set_foreground((255, 255, 255))
    pdb.gimp_edit_fill(layer, FILL_FOREGROUND)

    # Deselect
    pdb.gimp_selection_none(img)

    pdb.gimp_image_undo_group_end(img)

register(
    "python_fu_remove_yellow_lines",
    "Remove yellow lines (fuzzy match)",
    "Selects pixels near yellow shades and replaces them with white",
    "Your Name",
    "Your Name",
    "2025",
    "Remove Yellow Lines",
    "*",  # Works on all image types
    [
        (PF_IMAGE, "img", "Input image", None),
        (PF_DRAWABLE, "layer", "Input layer", None),
    ],
    [],
    remove_yellow_lines,
    menu="<Image>/Filters/Custom"
)

main()

from typing import Tuple
from color_defs import base_colors
from struct import unpack


class State:
    tag: str = "STATE"

    def __init__(self, value: str | bool | int, name: str = ""):
        self.name: str = name
        self.value: str = str(value)
        self.type: str = "unknown"
        if type(value) == str:
            self.type = "string"
        elif type(value) == bool:
            self.type = "boolean"
        elif type(value) == int:
            self.type = "int"


class Wrapped:
    tag: str = "WRAPPED_OPTION"

    def __init__(self, *states: State):
        self.states: Tuple[State, ...] = states
        self.classname = "ghidra.framework.options.Wrapped{}".format(
            self.__class__.__name__
        )


class Color(Wrapped):
    def __init__(self, color: str, alpha: int = 100):
        split_color = [color[i : i + 2] for i in range(0, len(color), 2)]
        clamped_alpha = max(min(alpha, 100), 0)
        normalized_alpha = float(clamped_alpha) / 100.0
        hex_alpha = int(255 * normalized_alpha)
        final_color_string = (
            f"{split_color[2]}{split_color[1]}{split_color[0]}{hex_alpha:x}"
        )
        hex_bytes = bytes.fromhex(final_color_string)
        converted_hex = unpack("i", hex_bytes)[0]
        super().__init__(State(converted_hex, "color"))


class Font(Wrapped):
    def __init__(self, size: int, style: int, family: str):
        super().__init__(
            State(size, "size"), State(style, "style"), State(family, "family")
        )


class KeyStroke(Wrapped):
    def __init__(self, keyCode: int, modifiers: int):
        super().__init__(State(keyCode, "KeyCode"), State(modifiers, "Modifiers"))


preferences = {
    "Listing Fields": {
        "Cursor Text Highlight.Highlight Color": Color(base_colors.selection),
        "Cursor Text Highlight.Scoped Write Highlight Color": Color(
            base_colors.selection
        ),
        "Cursor Text Highlight.Scoped Read Highlight Color": Color(
            base_colors.selection
        ),
        "Selection Colors.Selection Color": Color(base_colors.selection),
        "Selection Colors.Difference Color": Color(base_colors.selection),
        "Selection Colors.Highlight Color": Color(base_colors.selection),
        "Cursor.Cursor Color - Focused": Color(base_colors.fg),
        "Cursor.Cursor Color - Unfocused": Color(base_colors.selection, 40),
        "Cursor.Highlight Cursor Line Color": Color(base_colors.selection, 40),
    },
    "Decompiler": {
        "Display.Color for Keywords": Color(base_colors.pink),
        "Display.Background Color": Color(base_colors.bg),
        "Display.Color for Parameters": Color(base_colors.orange),
        "Display.Color for Constants": Color(base_colors.purple),
        "Display.Color for Current Variable Highlight": Color(base_colors.selection),
        "Display.Color Default": Color(base_colors.fg),
        "Display.Color for Types": Color(base_colors.cyan),
        "Display.Color for Variables": Color(base_colors.fg),
        "Display.Color for Comments": Color(base_colors.comment),
        "Display.Color for Function names": Color(base_colors.green),
        "Display.Font": Font(14, 0, "Fira Code"),
    },
    "Graph": {
        "Function Call Graph.Graph Background Color": Color(base_colors.comment),
        "Function Graph.Default Vertex Color": Color(base_colors.bg),
        "Function Graph.Graph Background Color": Color(base_colors.comment),
        "Function Graph.Edge Color - Conditional Jump ": Color(base_colors.green),
        "Function Graph.Edge Color - Conditional Jump Highlight": Color(
            base_colors.green, 50
        ),
        "Function Graph.Edge Color - Fallthrough ": Color(base_colors.yellow),
        "Function Graph.Edge Color - Fallthrough Highlight": Color(
            base_colors.yellow, 50
        ),
        "Function Graph.Edge Color - Unconditional Jump ": Color(base_colors.cyan),
        "Function Graph.Edge Color - Unconditional Jump Highlight": Color(
            base_colors.cyan, 50
        ),
    },
    "Search": {
        "Highlight Color for Current Match": Color(base_colors.orange, 80),
        "Highlight Color": Color(base_colors.white, 40),
    },
    "Listing Display": {
        "Background Color": Color(base_colors.bg),
        "Mnemonic Color": Color(base_colors.fg),
        "Bad Reference Address Color": Color(base_colors.red),
        "XRef Write Color": Color(base_colors.red),
        "Address Color": Color(base_colors.comment),
        "Function Parameters Color": Color(base_colors.orange),
        "Function Return Type Color": Color(base_colors.cyan),
        "Comment, Referenced Repeatable Color": Color(base_colors.comment),
        "Constant Color": Color(base_colors.purple),
        "XRef Other Color": Color(base_colors.comment),
        "EOL Comment Color": Color(base_colors.comment),
        "Labels, Primary Color": Color(base_colors.pink),
        "Function Tag Color": Color(base_colors.orange),
        "Bytes Color": Color(base_colors.cyan),
        "Post-Comment Color": Color(base_colors.comment),
        "Function Call-Fixup Color": Color(base_colors.purple, 50),
        "Plate Comment Color": Color(base_colors.comment),
        "Labels, Unreferenced Color": Color(base_colors.red, 50),
        "Entry Point Color": Color(base_colors.orange),
        "Pre-Comment Color": Color(base_colors.comment),
        "Mnemonic, Override Color": Color(base_colors.cyan),
        "External Reference, Resolved Color": Color(base_colors.green),
        "Parameter, Dynamic Storage Color": Color(base_colors.orange, 50),
        "Parameter, Custom Storage Color": Color(base_colors.green, 50),
        "Underline Color": Color(base_colors.purple, 50),
        "Field Name Color": Color(base_colors.fg),
        "XRef Read Color": Color(base_colors.cyan),
        "Separator Color": Color(base_colors.fg),
        "Version Track Color": Color(base_colors.purple, 50),
        "Comment, Automatic Color": Color(base_colors.comment),
        "XRef Color": Color(base_colors.green),
        "Variable Color": Color(base_colors.fg),
        "Flow Arrow, Active Color": Color(base_colors.green, 50),
        "Flow Arrow, Not Active Color": Color(base_colors.red, 50),
        "Labels, Local Color": Color(base_colors.cyan),
        "Function Name Color": Color(base_colors.green),
        "Comment, Repeatable Color": Color(base_colors.comment),
        "BASE FONT": Font(14, 0, "Fira Code"),
    },
    "Comments": {"Enter accepts comment": State(True)},
}

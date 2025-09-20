from enum import Enum
from htmlnode import *
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            isinstance(other, TextNode)
            and self.text_type == other.text_type
            and self.text == other.text
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(node: TextNode):
    if node.text_type == TextType.TEXT:
        return LeafNode(value=node.text)
    if node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=node.text)
    if node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=node.text)
    if node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=node.text)
    if node.text_type == TextType.LINK:
        return LeafNode(tag="a", value=node.text, props={"href": node.url})
    if node.text_type == TextType.IMAGE:
        return LeafNode(tag="img", props={"src": node.url, "alt": node.text})
    raise Exception("Not a supported TextType")


def split_nodes_delimiter(old_nodes, delimiter, text_type, *, drop_trailing_empty=False):
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        # Build alternating TEXT / formatted nodes
        chunk = []
        for i, part in enumerate(parts):
            current_type = text_type if i % 2 else TextType.TEXT
            chunk.append(TextNode(part, current_type))

        # Optionally drop the trailing empty TEXT node
        if drop_trailing_empty and chunk and \
           chunk[-1].text_type == TextType.TEXT and chunk[-1].text == "":
            chunk.pop()

        new_nodes.extend(chunk)
    return new_nodes



def extract_markdown_images(text):
    pattern = r'!\[(.*?)\]\((.*?)\)'
    return re.findall(pattern, text)


def extract_markdown_links(text):
    pattern = r'(?<!!)\[(.*?)\]\((.*?)\)'  # ignore images
    return re.findall(pattern, text)


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_images(text)

        if not matches:
            new_nodes.append(node)
            continue

        curr_index = 0
        for alt, src in matches:
            pattern = f"![{alt}]({src})"
            index = text.find(pattern, curr_index)

            if index > curr_index:
                new_nodes.append(TextNode(text[curr_index:index], TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.IMAGE, src))
            curr_index = index + len(pattern)

        if curr_index < len(text):
            new_nodes.append(TextNode(text[curr_index:], TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        matches = extract_markdown_links(text)

        if not matches:
            new_nodes.append(node)
            continue

        curr_index = 0
        for alt, href in matches:
            pattern = f"[{alt}]({href})"
            index = text.find(pattern, curr_index)

            if index > curr_index:
                new_nodes.append(TextNode(text[curr_index:index], TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.LINK, href))
            curr_index = index + len(pattern)

        if curr_index < len(text):
            new_nodes.append(TextNode(text[curr_index:], TextType.TEXT))
    return new_nodes


def text_to_textnodes(text: str):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    # Drop the trailing empty TEXT created by a terminal `code` segment
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE, drop_trailing_empty=True)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown: str) -> list[str]:
    """
    Split a raw Markdown string into block strings.

    - Blocks are separated by one or more blank lines (which may contain spaces/tabs).
    - Leading/trailing whitespace is stripped from each block.
    - Empty blocks are removed.
    """
    if not markdown:
        return []

    # Normalize newlines
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")

    # Split on one or more blank lines (lines that may contain only spaces/tabs)
    raw_blocks = re.split(r"\n[ \t]*\n+", text)

    # Strip each block and drop empties
    blocks = [b.strip() for b in raw_blocks if b.strip()]

    return blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block: str) -> BlockType:
    """
    Determine the Markdown block type.

    Assumes `block` has already had leading/trailing whitespace stripped.
    """
    if not block:
        return BlockType.PARAGRAPH

    # Code block: starts with ``` and ends with ```
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    # Heading: 1–6 '#' followed by a space, then text
    if re.match(r"^(#{1,6})\s+.+$", block):
        return BlockType.HEADING

    lines = block.split("\n")

    # Quote: every line starts with '>'
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    # Unordered list: every line starts with "- " (dash + space)
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: lines start with "1. ", "2. ", ... incrementing by 1
    is_ordered = True
    for i, line in enumerate(lines, start=1):
        if not line.startswith(f"{i}. "):
            is_ordered = False
            break
    if is_ordered and len(lines) > 0:
        return BlockType.ORDERED_LIST

    # Default: paragraph
    return BlockType.PARAGRAPH


def text_to_children(text: str):
    """
    Convert a string with inline markdown into a list of HTMLNodes,
    using your existing inline pipeline (TextNode -> HTMLNode).
    """
    nodes = text_to_textnodes(text)
    return [text_node_to_html_node(n) for n in nodes]

# ---------- per-block renderers ----------
def _render_heading(block: str) -> ParentNode:
    # Heading: 1–6 '#' + space
    m = re.match(r"^(#{1,6})\s+(.*)$", block)
    level = len(m.group(1))
    content = m.group(2)
    return ParentNode(f"h{level}", text_to_children(content))

def _render_paragraph(block: str) -> ParentNode:
    # Collapse internal line breaks into single spaces for paragraphs
    collapsed = " ".join(block.splitlines())
    return ParentNode("p", text_to_children(collapsed))


def _render_quote(block: str) -> ParentNode:
    # Every line starts with '>' possibly followed by space
    lines = block.split("\n")
    stripped = [re.sub(r"^>\s?", "", line) for line in lines]
    # Join with newlines to preserve line breaks inside the quote
    content = "\n".join(stripped)
    return ParentNode("blockquote", text_to_children(content))

def _render_ul(block: str) -> ParentNode:
    # Each line starts with "- "
    lines = [re.sub(r"^- ", "", line) for line in block.split("\n")]
    li_children = [ParentNode("li", text_to_children(line)) for line in lines]
    return ParentNode("ul", li_children)

def _render_ol(block: str) -> ParentNode:
    # Lines like "1. item", "2. item", incrementing numbers
    lines = [re.sub(r"^\d+\.\s", "", line) for line in block.split("\n")]
    li_children = [ParentNode("li", text_to_children(line)) for line in lines]
    return ParentNode("ol", li_children)

def _render_code(block: str) -> ParentNode:
    lines = block.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    code_text = "\n".join(lines)
    # Ensure trailing newline
    if not code_text.endswith("\n"):
        code_text += "\n"
    code_leaf = LeafNode(tag="code", value=code_text)
    return ParentNode("pre", [code_leaf])

# ---------- main entry ----------
def markdown_to_html_node(markdown: str) -> ParentNode:
    """
    Convert a full Markdown document into a single parent HTML node (<div>),
    with one child per block.
    """
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        btype = block_to_block_type(block)
        if btype.name == "HEADING":
            children.append(_render_heading(block))
        elif btype.name == "QUOTE":
            children.append(_render_quote(block))
        elif btype.name == "UNORDERED_LIST":
            children.append(_render_ul(block))
        elif btype.name == "ORDERED_LIST":
            children.append(_render_ol(block))
        elif btype.name == "CODE":
            children.append(_render_code(block))
        else:  # PARAGRAPH
            children.append(_render_paragraph(block))

    # Wrap all block nodes in a single container <div>
    return ParentNode("div", children)

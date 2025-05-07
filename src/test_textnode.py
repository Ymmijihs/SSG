import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual(node, node2)

    def test_eq_false(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq_false2(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node2", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.ITALIC, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.ITALIC, "https://www.boot.dev")
        self.assertEqual(node, node2)

    def test_repr(self):
        node = TextNode("This is a text node", TextType.TEXT, "https://www.boot.dev")
        self.assertEqual(
            "TextNode(This is a text node, text, https://www.boot.dev)", repr(node)
        )

def test_text(self):
    node = TextNode("This is a text node", TextType.TEXT)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, None)
    self.assertEqual(html_node.value, "This is a text node")

def test_text_node_as_bold(self):
    node = TextNode("This is bold text", TextType.BOLD)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "b")
    self.assertEqual(html_node.value, "This is bold text")

def test_text_node_as_italic(self):
    node = TextNode("This is italic text", TextType.ITALIC)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "i")
    self.assertEqual(html_node.value, "This is italic text")

def test_text_node_as_code(self):
    node = TextNode("This is a code snippet", TextType.CODE)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "code")
    self.assertEqual(html_node.value, "This is a code snippet")

def test_text_node_as_link(self):
    node = TextNode("Click here", TextType.LINK)
    # Assuming self.href is set in the class context, for example as "http://example.com"
    self.href = "http://example.com"
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "a")
    self.assertEqual(html_node.value, "Click here")
    self.assertEqual(html_node.props, {"href": "http://example.com"})  # Check href property

def test_text_node_as_image(self):
    node = TextNode("Image description", TextType.IMAGE)
    # Assuming self.src and self.alt are set in the class context
    self.src = "image.png"
    self.alt = "An example image"
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, "img")
    self.assertEqual(html_node.props, {"src": "image.png", "alt": "An example image"})  # Check props

def test_text_node_unsupported_type(self):
    node = TextNode("Unsupported text", TextType.UNSUPPORTED)  # Assuming UNSUPPORTED is a defined enum
    with self.assertRaises(Exception) as context:
        text_node_to_html_node(node)
    self.assertEqual(str(context.exception), "Not a supported TextType")

    def test_split_nodes_delimiter_basic(self):
        node = TextNode("This is a `code block` in text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" in text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_nodes_delimiter_with_multiple(self):
        node = TextNode("Using `inline code` and **bold text**", TextType.TEXT)
        new_nodes_code = split_nodes_delimiter([node], "`", TextType.CODE)
        # Handling the inline code
        expected_code = [
            TextNode("Using ", TextType.TEXT),
            TextNode("inline code", TextType.CODE),
            TextNode(" and **bold text**", TextType.TEXT),
        ]
        self.assertEqual(new_nodes_code, expected_code)

        # Now handling bold text
        node_bold = TextNode("Using `code` and **bold text**", TextType.TEXT)
        new_nodes_bold = split_nodes_delimiter([node_bold], "**", TextType.BOLD)
        expected_bold = [
            TextNode("Using `code` and ", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode("", TextType.TEXT),  # Expecting an empty text for trailing
        ]
        self.assertEqual(new_nodes_bold, expected_bold)

    def test_split_nodes_delimiter_no_delimiter(self):
        node = TextNode("Just a simple text without delimiter", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("Just a simple text without delimiter", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

if __name__ == "__main__":
    unittest.main()

import unittest
import textwrap
from textnode import markdown_to_html_node


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = (
            "This is **bolded** paragraph\n"
            "text in a p\n"
            "tag here\n\n"
            "This is another paragraph with _italic_ text and `code` here\n"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p>"
            "<p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        # use dedent to avoid stray indentation; fenced code must be preserved exactly
        md = textwrap.dedent("""\
            ```
            This is text that _should_ remain
            the **same** even with inline stuff
            ```
            """)
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\n"
            "the **same** even with inline stuff\n"
            "</code></pre></div>",
        )

    def test_heading_levels(self):
        md = "# H1 title\n\n###### H6 title"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>H1 title</h1><h6>H6 title</h6></div>")

    def test_unordered_list(self):
        md = "- first **bold**\n- second _ital_\n- third `code`"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul>"
            "<li>first <b>bold</b></li>"
            "<li>second <i>ital</i></li>"
            "<li>third <code>code</code></li>"
            "</ul></div>",
        )

    def test_ordered_list(self):
        md = "1. one\n2. two\n3. three"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ol><li>one</li><li>two</li><li>three</li></ol></div>")

    def test_blockquote(self):
        md = "> quoted **bold**\n> still quoted _ital_"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>quoted <b>bold</b>\nstill quoted <i>ital</i></blockquote></div>",
        )

    def test_links_and_images_in_paragraph(self):
        md = "A [link](https://example.com) and an ![alt](img.png) here."
        node = markdown_to_html_node(md)
        html = node.to_html()
        # image should render as <img src="img.png" alt="alt"/> (or <img ...></img> if not self-closing)
        # paragraph should inline-parse link and image
        self.assertIn('<p>A <a href="https://example.com">link</a> and an ', html)
        self.assertTrue(
            '<img src="img.png" alt="alt"' in html
        )  # allow either self-closing or paired
        self.assertTrue(html.endswith("</div>"))

    def test_mixed_document(self):
        md = (
            "# Title\n\n"
            "Intro paragraph with a [link](https://example.com).\n\n"
            "- item one\n- item two\n\n"
            "1. first\n2. second\n\n"
            "> quote line one\n> quote line two\n\n"
            "```\ncode_inline_should_not_parse **nor** _this_\n```\n"
        )
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div>"
            "<h1>Title</h1>"
            "<p>Intro paragraph with a <a href=\"https://example.com\">link</a>.</p>"
            "<ul><li>item one</li><li>item two</li></ul>"
            "<ol><li>first</li><li>second</li></ol>"
            "<blockquote>quote line one\nquote line two</blockquote>"
            "<pre><code>code_inline_should_not_parse **nor** _this_\n</code></pre>"
            "</div>",
        )


if __name__ == "__main__":
    unittest.main()

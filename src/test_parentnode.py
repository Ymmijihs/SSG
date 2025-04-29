import unittest
from htmlnode import *


class TestParentNode(unittest.TestCase):

	def test_to_html_with_empty_children(self):
		parent_node = ParentNode("div", [])
		with self.assertRaises(ValueError) as context:
			parent_node.to_html()
		self.assertEqual(str(context.exception), "Children are missing")

	def test_to_html_with_no_tag(self):
		child_node = LeafNode("p", "text")
		parent_node = ParentNode(None, [child_node])
		with self.assertRaises(ValueError) as context:
			parent_node.to_html()
		self.assertEqual(str(context.exception), "Tag is missing")

	def test_to_html_with_multiple_children(self):
		child_node1 = LeafNode("p", "child 1")
		child_node2 = LeafNode("p", "child 2")
		parent_node = ParentNode("div", [child_node1, child_node2])
		self.assertEqual(
			parent_node.to_html(),
			"<div><p>child 1</p><p>child 2</p></div>",
			)

	def test_to_html_with_nested_children(self):
		child_node1 = LeafNode("span", "child 1")
		grandchild_node = LeafNode("b", "grandchild")
		child_node2 = ParentNode("span", [grandchild_node])
		parent_node = ParentNode("div", [child_node1, child_node2])
		self.assertEqual(
			parent_node.to_html(),
			"<div><span>child 1</span><span><b>grandchild</b></span></div>",
			)

	def test_to_html_with_complex_structure(self):
		grandchild_node1 = LeafNode("em", "first")
		grandchild_node2 = LeafNode("em", "second")
		child_node1 = ParentNode("span", [grandchild_node1])
		child_node2 = ParentNode("span", [grandchild_node2])
		parent_node = ParentNode("div", [child_node1, child_node2])
		self.assertEqual(
			parent_node.to_html(),
			"<div><span><em>first</em></span><span><em>second</em></span></div>",
			)


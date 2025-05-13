from enum import Enum
from htmlnode import LeafNode
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
			self.text_type == other.text_type
			and self.text == other.text
			and self.url == other.url
			)

	def __repr__(self):
		return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

	def text_node_to_html_node(text_node):
		if self.text_type == TEXT:
			return LeafNode(value=self.text)
		if self.text_type == BOLD:
			return LeafNode(tag="b", value=self.text)
		if self.text_type == ITALIC:
			return LeafNode(tag="i", value=self.text)
		if self.text_type == CODE:
			return LeafNode(tag="code", value=self.text)
		if self.text_type == LINK:
			return LeafNode(tag="a", value=self.text, props="href")
		if self.text_type == IMAGE:
			return LeafNode(tag="img",props=("src","alt"))
		else:
			raise Exception("Not a supported TextType")



def split_nodes_delimiter(old_nodes, delimiter, text_type):
	new_nodes = []
	for node in old_nodes:
		if isinstance(node, TextNode):
			parts = node.text.split(delimiter)
			for i, part in enumerate(parts):
				current_type = text_type if i % 2 != 0 else TextType.TEXT
				new_nodes.append(TextNode(part, current_type))
	return new_nodes

def extract_markdown_images(text):
	pattern = r'!\[(.*?)\]\((.*?)\)'
	matches = re.findall(pattern, text)
	return matches

def extract_markdown_links(text):
	pattern = r'\[(.*?)\]\((.*?)\)'
	matches = re.findall(pattern, text)
	return matches

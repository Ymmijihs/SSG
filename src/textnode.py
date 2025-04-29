from enum import Enum
from htmlnode import LeafNode


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


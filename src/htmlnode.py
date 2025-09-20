class HTMLNode:
	def __init__(self, tag=None, value=None, children=None, props=None):
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def to_html(self):
		raise NotImplementedError("to_html method not implemented")

	def props_to_html(self):
		if self.props is None:
			return ""
		props_html = ""
		for prop in self.props:
			props_html += f' {prop}="{self.props[prop]}"'
		return props_html

	def __repr__(self):
		return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        props_html = self.props_to_html()

        # Plain text node (no tag)
        if not self.tag:
            if self.value is None:
                raise ValueError("Value is missing for plain text node")
            return f"{self.value}"

        # HTML void elements: render self-closing when value is None
        void_tags = {
            "area", "base", "br", "col", "embed", "hr", "img",
            "input", "link", "meta", "param", "source", "track", "wbr",
        }
        if self.value is None or self.tag in void_tags:
            return f"<{self.tag}{props_html}/>"

        # Normal element with value
        return f"<{self.tag}{props_html}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
	def __init__(self, tag, children, props=None):
		super().__init__(tag=tag, children=children, props=props)

	def to_html(self):
		if self.tag is None:
			raise ValueError("Tag is missing")
		if self.children is None or len(self.children) ==0:
			raise ValueError("Children are missing")
		html_string = f"<{self.tag}>"
		for child in self.children:
			childstring = child.to_html()
			html_string += childstring
		html_string += f"</{self.tag}>"
		return html_string

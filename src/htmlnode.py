from textnode import TextNode, TextType


class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is None:
            return ""
        return "".join(f' {key}="{value}"' for key, value in self.props.items())

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("leaf node must have a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("parent node must have a tag value")
        if self.children is None:
            raise ValueError("parent node must have children")
        html_string = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            html_string += child.to_html()
        html_string += f"</{self.tag}>"
        return html_string

    def __repr__(self):
        return f"ParentNode({self.tag}, {self.children}, {self.props})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        tag = None
        value = text_node.text
        props = None
    elif text_node.text_type == TextType.BOLD:
        tag = "b"
        value = text_node.text
        props = None
    elif text_node.text_type == TextType.ITALIC:
        tag = "i"
        value = text_node.text
        props = None
    elif text_node.text_type == TextType.CODE:
        tag = "code"
        value = text_node.text
        props = None
    elif text_node.text_type == TextType.LINK:
        tag = "a"
        value = text_node.text
        props = {"href": text_node.url} if text_node.url else None
    elif text_node.text_type == TextType.IMAGE:
        tag = "img"
        value = ""
        props = (
            {"src": text_node.url, "alt": text_node.text}
            if text_node.url
            else {"alt": text_node.text}
        )
    else:
        raise ValueError(f"Unknown TextType: {text_node.text_type}")

    return LeafNode(tag, value, props)

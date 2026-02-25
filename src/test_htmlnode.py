import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_single(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(
            tag="a",
            props={"href": "https://example.com", "target": "_blank"},
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://example.com" target="_blank"',
        )

    def test_props_to_html_none(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), "")

    def test_defaults_are_none(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_tag_and_value(self):
        node = HTMLNode(tag="p", value="Hello, world!")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello, world!")

    def test_children(self):
        child1 = HTMLNode(tag="b", value="bold")
        child2 = HTMLNode(tag="i", value="italic")
        parent = HTMLNode(tag="div", children=[child1, child2])
        self.assertEqual(len(parent.children), 2)
        self.assertEqual(parent.children[0].tag, "b")
        self.assertEqual(parent.children[1].tag, "i")

    def test_to_html_raises(self):
        node = HTMLNode(tag="p", value="text")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode(tag="a", value="link", props={"href": "https://example.com"})
        self.assertEqual(
            repr(node),
            "HTMLNode(a, link, None, {'href': 'https://example.com'})",
        )


class TestLeafNode(unittest.TestCase):
    def test_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click me!</a>')

    def test_to_html_no_tag(self):
        node = LeafNode(None, "Just raw text")
        self.assertEqual(node.to_html(), "Just raw text")

    def test_to_html_no_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_children_always_none(self):
        node = LeafNode("p", "text")
        self.assertIsNone(node.children)

    def test_props_default_none(self):
        node = LeafNode("p", "text")
        self.assertIsNone(node.props)

    def test_to_html_multiple_props(self):
        node = LeafNode(
            "a", "link", {"href": "https://example.com", "target": "_blank"}
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com" target="_blank">link</a>',
        )

    def test_repr(self):
        node = LeafNode("p", "hello")
        self.assertEqual(repr(node), "LeafNode(p, hello, None)")

    def test_is_subclass_of_htmlnode(self):
        node = LeafNode("p", "text")
        self.assertIsInstance(node, HTMLNode)


class TestParentNode(unittest.TestCase):
    def test_to_html_single_child(self):
        node = ParentNode("p", [LeafNode("b", "Bold text")])
        self.assertEqual(node.to_html(), "<p><b>Bold text</b></p>")

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_nested_parent_nodes(self):
        node = ParentNode(
            "div",
            [
                ParentNode("p", [LeafNode("b", "Bold")]),
                ParentNode("p", [LeafNode("i", "Italic")]),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><p><b>Bold</b></p><p><i>Italic</i></p></div>",
        )

    def test_to_html_deeply_nested(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "section",
                    [
                        ParentNode(
                            "p",
                            [LeafNode("span", "deep text")],
                        )
                    ],
                )
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div><section><p><span>deep text</span></p></section></div>",
        )

    def test_to_html_no_tag_raises(self):
        node = ParentNode(None, [LeafNode("b", "Bold")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children_raises(self):
        node = ParentNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_empty_children(self):
        node = ParentNode("p", [])
        self.assertEqual(node.to_html(), "<p></p>")

    def test_to_html_with_props(self):
        node = ParentNode(
            "div",
            [LeafNode("p", "Hello")],
            {"class": "container", "id": "main"},
        )
        self.assertEqual(
            node.to_html(),
            '<div class="container" id="main"><p>Hello</p></div>',
        )

    def test_to_html_mixed_children(self):
        node = ParentNode(
            "div",
            [
                LeafNode(None, "raw text"),
                ParentNode("p", [LeafNode("b", "bold")]),
                LeafNode("i", "italic"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<div>raw text<p><b>bold</b></p><i>italic</i></div>",
        )

    def test_to_html_child_with_props(self):
        node = ParentNode(
            "nav",
            [
                LeafNode("a", "Home", {"href": "/"}),
                LeafNode("a", "About", {"href": "/about"}),
            ],
        )
        self.assertEqual(
            node.to_html(),
            '<nav><a href="/">Home</a><a href="/about">About</a></nav>',
        )

    def test_value_is_none(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsNone(node.value)

    def test_props_default_none(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsNone(node.props)

    def test_is_subclass_of_htmlnode(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsInstance(node, HTMLNode)

    def test_repr(self):
        child = LeafNode("b", "bold")
        node = ParentNode("p", [child])
        self.assertEqual(
            repr(node),
            f"ParentNode(p, [{repr(child)}], None)",
        )

    def test_headings(self):
        node = ParentNode(
            "h2",
            [
                LeafNode(None, "Normal "),
                LeafNode("b", "bold"),
                LeafNode(None, " text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<h2>Normal <b>bold</b> text</h2>",
        )


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_plain_text(self):
        node = text_node_to_html_node(TextNode("hello", TextType.TEXT))
        self.assertIsNone(node.tag)
        self.assertEqual(node.value, "hello")
        self.assertIsNone(node.props)
        self.assertEqual(node.to_html(), "hello")

    def test_bold(self):
        node = text_node_to_html_node(TextNode("bold text", TextType.BOLD))
        self.assertEqual(node.tag, "b")
        self.assertEqual(node.value, "bold text")
        self.assertIsNone(node.props)
        self.assertEqual(node.to_html(), "<b>bold text</b>")

    def test_italic(self):
        node = text_node_to_html_node(TextNode("italic text", TextType.ITALIC))
        self.assertEqual(node.tag, "i")
        self.assertEqual(node.value, "italic text")
        self.assertIsNone(node.props)
        self.assertEqual(node.to_html(), "<i>italic text</i>")

    def test_code(self):
        node = text_node_to_html_node(TextNode("print('hi')", TextType.CODE))
        self.assertEqual(node.tag, "code")
        self.assertEqual(node.value, "print('hi')")
        self.assertIsNone(node.props)
        self.assertEqual(node.to_html(), "<code>print('hi')</code>")

    def test_link(self):
        node = text_node_to_html_node(
            TextNode("Click me", TextType.LINK, "https://example.com")
        )
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Click me")
        self.assertEqual(node.props, {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click me</a>')

    def test_link_no_url(self):
        node = text_node_to_html_node(TextNode("Click me", TextType.LINK))
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "Click me")
        self.assertIsNone(node.props)

    def test_image(self):
        node = text_node_to_html_node(
            TextNode("alt text", TextType.IMAGE, "https://example.com/img.png")
        )
        self.assertEqual(node.tag, "img")
        self.assertEqual(node.value, "")
        self.assertEqual(
            node.props, {"src": "https://example.com/img.png", "alt": "alt text"}
        )
        self.assertEqual(
            node.to_html(),
            '<img src="https://example.com/img.png" alt="alt text"></img>',
        )

    def test_image_no_url(self):
        node = text_node_to_html_node(TextNode("alt text", TextType.IMAGE))
        self.assertEqual(node.tag, "img")
        self.assertEqual(node.value, "")
        self.assertEqual(node.props, {"alt": "alt text"})

    def test_returns_leaf_node(self):
        node = text_node_to_html_node(TextNode("text", TextType.TEXT))
        self.assertIsInstance(node, LeafNode)

    def test_unknown_type_raises(self):
        fake_node = TextNode("text", "unknown_type")
        with self.assertRaises(ValueError):
            text_node_to_html_node(fake_node)


if __name__ == "__main__":
    unittest.main()

import unittest

from textnode import (
    TextNode,
    TextType,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a not text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_type_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_basic_code_split(self):
        node = TextNode("hello `code` world", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("hello ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" world", TextType.TEXT),
            ],
        )

    def test_basic_bold_split(self):
        node = TextNode("hello **bold** world", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("hello ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" world", TextType.TEXT),
            ],
        )

    def test_basic_italic_split(self):
        node = TextNode("hello *italic* world", TextType.TEXT)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(
            result,
            [
                TextNode("hello ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" world", TextType.TEXT),
            ],
        )

    def test_multiple_delimited_sections(self):
        node = TextNode("a `b` c `d` e", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("b", TextType.CODE),
                TextNode(" c ", TextType.TEXT),
                TextNode("d", TextType.CODE),
                TextNode(" e", TextType.TEXT),
            ],
        )

    def test_delimiter_at_start(self):
        node = TextNode("`code` after", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("code", TextType.CODE),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_delimiter_at_end(self):
        node = TextNode("before `code`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_only_delimited_content(self):
        node = TextNode("`code`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [TextNode("code", TextType.CODE)],
        )

    def test_no_delimiter_in_text_node(self):
        node = TextNode("no delimiters here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [TextNode("no delimiters here", TextType.TEXT)],
        )

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_non_text_node_preserves_all_fields(self):
        node = TextNode("click here", TextType.LINK, "https://example.com")
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "click here")
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual(result[0].url, "https://example.com")

    def test_multiple_nodes_mixed_types(self):
        nodes = [
            TextNode("hello `code` world", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
            TextNode("more `code` here", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("hello ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" world", TextType.TEXT),
                TextNode("already bold", TextType.BOLD),
                TextNode("more ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_empty_list(self):
        result = split_nodes_delimiter([], "`", TextType.CODE)
        self.assertEqual(result, [])

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [])

    def test_unmatched_delimiter_raises(self):
        node = TextNode("hello `unclosed", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_all_non_text_nodes_pass_through(self):
        nodes = [
            TextNode("a", TextType.BOLD),
            TextNode("b", TextType.ITALIC),
            TextNode("c", TextType.CODE),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(result, nodes)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_single_image(self):
        text = "Here is an image ![alt text](https://example.com/image.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("alt text", "https://example.com/image.png")])

    def test_multiple_images(self):
        text = "![first](https://a.com/1.png) and ![second](https://b.com/2.jpg)"
        result = extract_markdown_images(text)
        self.assertEqual(
            result,
            [("first", "https://a.com/1.png"), ("second", "https://b.com/2.jpg")],
        )

    def test_no_images(self):
        text = "This is plain text with no images"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_empty_string(self):
        result = extract_markdown_images("")
        self.assertEqual(result, [])

    def test_empty_alt_text(self):
        text = "![](https://example.com/image.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("", "https://example.com/image.png")])

    def test_empty_url(self):
        text = "![alt text]()"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("alt text", "")])

    def test_does_not_match_links(self):
        text = "[link text](https://example.com)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_image_among_other_markdown(self):
        text = "Some **bold** text and ![img](https://example.com/img.png) and *italic*"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("img", "https://example.com/img.png")])

    def test_image_with_spaces_in_alt(self):
        text = "![a longer alt text here](https://example.com/photo.jpg)"
        result = extract_markdown_images(text)
        self.assertEqual(
            result, [("a longer alt text here", "https://example.com/photo.jpg")]
        )

    def test_nested_brackets_in_alt_no_match(self):
        text = "![alt [with] brackets](https://example.com/img.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_nested_parens_in_url_no_match(self):
        text = "![alt](https://example.com/path(1).png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_multiple_images_no_space_between(self):
        text = "![a](https://a.com/1.png)![b](https://b.com/2.png)"
        result = extract_markdown_images(text)
        self.assertEqual(
            result,
            [("a", "https://a.com/1.png"), ("b", "https://b.com/2.png")],
        )

    def test_malformed_missing_closing_paren(self):
        text = "![alt](https://example.com/img.png"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_malformed_missing_closing_bracket(self):
        text = "![alt text(https://example.com/img.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [])

    def test_url_with_query_string(self):
        text = "![img](https://example.com/img.png?width=100&height=200)"
        result = extract_markdown_images(text)
        self.assertEqual(
            result, [("img", "https://example.com/img.png?width=100&height=200")]
        )

    def test_url_with_fragment(self):
        text = "![img](https://example.com/img.png#section)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("img", "https://example.com/img.png#section")])

    def test_url_with_encoded_spaces(self):
        text = "![img](https://example.com/my%20image.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("img", "https://example.com/my%20image.png")])


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_single_link(self):
        text = "Here is a [link](https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com")])

    def test_multiple_links(self):
        text = "[first](https://a.com) and [second](https://b.com)"
        result = extract_markdown_links(text)
        self.assertEqual(
            result, [("first", "https://a.com"), ("second", "https://b.com")]
        )

    def test_no_links(self):
        text = "This is plain text with no links"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_empty_string(self):
        result = extract_markdown_links("")
        self.assertEqual(result, [])

    def test_empty_anchor_text(self):
        text = "[](https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("", "https://example.com")])

    def test_empty_url(self):
        text = "[link text]()"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link text", "")])

    def test_does_not_match_images(self):
        text = "![alt text](https://example.com/image.png)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_link_next_to_image(self):
        text = "![img](https://img.com/pic.png) [link](https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com")])

    def test_link_with_spaces_in_text(self):
        text = "[click here for more](https://example.com/page)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("click here for more", "https://example.com/page")])

    def test_link_among_other_markdown(self):
        text = "Some **bold** and [a link](https://example.com) and *italic*"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("a link", "https://example.com")])

    def test_nested_brackets_in_text_no_match(self):
        text = "[text [with] brackets](https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_nested_parens_in_url_no_match(self):
        text = "[link](https://example.com/path(1))"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_multiple_links_no_space_between(self):
        text = "[a](https://a.com)[b](https://b.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("a", "https://a.com"), ("b", "https://b.com")])

    def test_double_bang_before_bracket_no_match(self):
        # !! still has ! immediately before [, so the lookbehind rejects it
        text = "!![link](https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_malformed_missing_closing_paren(self):
        text = "[link](https://example.com"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_malformed_missing_closing_bracket(self):
        text = "[link text(https://example.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [])

    def test_url_with_query_string(self):
        text = "[link](https://example.com/page?foo=bar&baz=1)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com/page?foo=bar&baz=1")])

    def test_url_with_fragment(self):
        text = "[link](https://example.com/page#section)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com/page#section")])

    def test_url_with_encoded_spaces(self):
        text = "[link](https://example.com/my%20page)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com/my%20page")])


class TestExtractMarkdownMixed(unittest.TestCase):
    def test_mixed_images_and_links_extract_images_only(self):
        text = "![img](https://img.com/pic.png) and [link](https://example.com) and ![img2](https://img.com/pic2.png)"
        result = extract_markdown_images(text)
        self.assertEqual(
            result,
            [("img", "https://img.com/pic.png"), ("img2", "https://img.com/pic2.png")],
        )

    def test_mixed_images_and_links_extract_links_only(self):
        text = "![img](https://img.com/pic.png) and [link](https://example.com) and ![img2](https://img.com/pic2.png)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "https://example.com")])

    def test_mixed_counts_are_correct(self):
        text = "[a](1) ![b](2) [c](3) ![d](4) [e](5)"
        images = extract_markdown_images(text)
        links = extract_markdown_links(text)
        self.assertEqual(len(images), 2)
        self.assertEqual(len(links), 3)


class TestSplitNodesImage(unittest.TestCase):
    def test_single_image(self):
        node = TextNode(
            "before ![alt](https://example.com/img.png) after", TextType.TEXT
        )
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_multiple_images(self):
        node = TextNode(
            "a ![first](https://a.com/1.png) b ![second](https://b.com/2.png) c",
            TextType.TEXT,
        )
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("first", TextType.IMAGE, "https://a.com/1.png"),
                TextNode(" b ", TextType.TEXT),
                TextNode("second", TextType.IMAGE, "https://b.com/2.png"),
                TextNode(" c", TextType.TEXT),
            ],
        )

    def test_image_at_start(self):
        node = TextNode("![img](https://example.com/img.png) after", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_image_at_end(self):
        node = TextNode("before ![img](https://example.com/img.png)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
            ],
        )

    def test_only_image(self):
        node = TextNode("![img](https://example.com/img.png)", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
            ],
        )

    def test_no_images(self):
        node = TextNode("just plain text", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("just plain text", TextType.TEXT)])

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_non_text_node_with_image_syntax_passes_through(self):
        node = TextNode("![img](https://example.com/img.png)", TextType.BOLD)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [TextNode("![img](https://example.com/img.png)", TextType.BOLD)],
        )

    def test_multiple_nodes(self):
        nodes = [
            TextNode("before ![a](https://a.com/1.png) after", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode("more ![b](https://b.com/2.png) text", TextType.TEXT),
        ]
        result = split_nodes_image(nodes)
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://a.com/1.png"),
                TextNode(" after", TextType.TEXT),
                TextNode("bold text", TextType.BOLD),
                TextNode("more ", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "https://b.com/2.png"),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_empty_list(self):
        result = split_nodes_image([])
        self.assertEqual(result, [])

    def test_does_not_split_links(self):
        node = TextNode("a [link](https://example.com) b", TextType.TEXT)
        result = split_nodes_image([node])
        self.assertEqual(
            result, [TextNode("a [link](https://example.com) b", TextType.TEXT)]
        )

    def test_images_no_space_between(self):
        node = TextNode(
            "![a](https://a.com/1.png)![b](https://b.com/2.png)", TextType.TEXT
        )
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("a", TextType.IMAGE, "https://a.com/1.png"),
                TextNode("", TextType.TEXT),
                TextNode("b", TextType.IMAGE, "https://b.com/2.png"),
            ],
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_single_link(self):
        node = TextNode("before [link](https://example.com) after", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_multiple_links(self):
        node = TextNode(
            "a [first](https://a.com) b [second](https://b.com) c",
            TextType.TEXT,
        )
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.TEXT),
                TextNode("first", TextType.LINK, "https://a.com"),
                TextNode(" b ", TextType.TEXT),
                TextNode("second", TextType.LINK, "https://b.com"),
                TextNode(" c", TextType.TEXT),
            ],
        )

    def test_link_at_start(self):
        node = TextNode("[link](https://example.com) after", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" after", TextType.TEXT),
            ],
        )

    def test_link_at_end(self):
        node = TextNode("before [link](https://example.com)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_only_link(self):
        node = TextNode("[link](https://example.com)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_no_links(self):
        node = TextNode("just plain text", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("just plain text", TextType.TEXT)])

    def test_non_text_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("already bold", TextType.BOLD)])

    def test_non_text_node_with_link_syntax_passes_through(self):
        node = TextNode("[link](https://example.com)", TextType.BOLD)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [TextNode("[link](https://example.com)", TextType.BOLD)],
        )

    def test_multiple_nodes(self):
        nodes = [
            TextNode("before [a](https://a.com) after", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode("more [b](https://b.com) text", TextType.TEXT),
        ]
        result = split_nodes_link(nodes)
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.TEXT),
                TextNode("a", TextType.LINK, "https://a.com"),
                TextNode(" after", TextType.TEXT),
                TextNode("bold text", TextType.BOLD),
                TextNode("more ", TextType.TEXT),
                TextNode("b", TextType.LINK, "https://b.com"),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_empty_list(self):
        result = split_nodes_link([])
        self.assertEqual(result, [])

    def test_does_not_split_images(self):
        node = TextNode("a ![img](https://example.com/img.png) b", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [TextNode("a ![img](https://example.com/img.png) b", TextType.TEXT)],
        )

    def test_links_no_space_between(self):
        node = TextNode("[a](https://a.com)[b](https://b.com)", TextType.TEXT)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("a", TextType.LINK, "https://a.com"),
                TextNode("", TextType.TEXT),
                TextNode("b", TextType.LINK, "https://b.com"),
            ],
        )


class TestTextToTextnodes(unittest.TestCase):
    def test_all_types(self):
        text = "This is **bold** and _italic_ and `code` and ![img](https://img.com/pic.png) and [link](https://example.com)"
        result = text_to_textnodes(text)
        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://img.com/pic.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_plain_text(self):
        result = text_to_textnodes("just plain text")
        self.assertEqual(result, [TextNode("just plain text", TextType.TEXT)])

    def test_only_bold(self):
        result = text_to_textnodes("**bold**")
        self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

    def test_only_italic(self):
        result = text_to_textnodes("_italic_")
        self.assertEqual(result, [TextNode("italic", TextType.ITALIC)])

    def test_only_code(self):
        result = text_to_textnodes("`code`")
        self.assertEqual(result, [TextNode("code", TextType.CODE)])

    def test_only_image(self):
        result = text_to_textnodes("![alt](https://example.com/img.png)")
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("alt", TextType.IMAGE, "https://example.com/img.png"),
            ],
        )

    def test_only_link(self):
        result = text_to_textnodes("[click](https://example.com)")
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("click", TextType.LINK, "https://example.com"),
            ],
        )

    def test_bold_at_start(self):
        result = text_to_textnodes("**bold** and text")
        self.assertEqual(
            result,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and text", TextType.TEXT),
            ],
        )

    def test_bold_at_end(self):
        result = text_to_textnodes("text and **bold**")
        self.assertEqual(
            result,
            [
                TextNode("text and ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
        )

    def test_multiple_bold(self):
        result = text_to_textnodes("**a** then **b**")
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.BOLD),
                TextNode(" then ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
            ],
        )

    def test_multiple_italic(self):
        result = text_to_textnodes("_a_ then _b_")
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.ITALIC),
                TextNode(" then ", TextType.TEXT),
                TextNode("b", TextType.ITALIC),
            ],
        )

    def test_bold_and_italic_adjacent(self):
        result = text_to_textnodes("**bold**_italic_")
        self.assertEqual(
            result,
            [
                TextNode("bold", TextType.BOLD),
                TextNode("italic", TextType.ITALIC),
            ],
        )

    def test_empty_string(self):
        result = text_to_textnodes("")
        self.assertEqual(result, [])

    def test_image_and_link_together(self):
        text = "![img](https://img.com/pic.png) and [link](https://example.com)"
        result = text_to_textnodes(text)
        self.assertEqual(
            result,
            [
                TextNode("", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://img.com/pic.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_unmatched_bold_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("this is **unclosed bold")

    def test_unmatched_italic_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("this is _unclosed italic")

    def test_unmatched_code_raises(self):
        with self.assertRaises(ValueError):
            text_to_textnodes("this is `unclosed code")


if __name__ == "__main__":
    unittest.main()

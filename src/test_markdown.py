import unittest

from markdown import markdown_to_html_node


class TestMarkdownToHtmlNode(unittest.TestCase):
    # --- Returns a div wrapper ---
    def test_returns_div_parent(self):
        result = markdown_to_html_node("Hello world")
        self.assertEqual(result.tag, "div")

    def test_single_paragraph_child_count(self):
        result = markdown_to_html_node("Hello world")
        self.assertEqual(len(result.children), 1)

    # --- Paragraph tests ---
    def test_paragraph(self):
        result = markdown_to_html_node("This is a paragraph.")
        self.assertEqual(result.to_html(), "<div><p>This is a paragraph.</p></div>")

    def test_paragraph_with_inline_bold(self):
        result = markdown_to_html_node("This is **bold** text.")
        self.assertEqual(
            result.to_html(), "<div><p>This is <b>bold</b> text.</p></div>"
        )

    def test_paragraph_with_inline_italic(self):
        result = markdown_to_html_node("This is _italic_ text.")
        self.assertEqual(
            result.to_html(), "<div><p>This is <i>italic</i> text.</p></div>"
        )

    def test_paragraph_with_inline_code(self):
        result = markdown_to_html_node("Use the `print` function.")
        self.assertEqual(
            result.to_html(), "<div><p>Use the <code>print</code> function.</p></div>"
        )

    def test_paragraph_with_link(self):
        result = markdown_to_html_node("Visit [boot.dev](https://boot.dev) today.")
        self.assertEqual(
            result.to_html(),
            '<div><p>Visit <a href="https://boot.dev">boot.dev</a> today.</p></div>',
        )

    def test_paragraph_with_image(self):
        result = markdown_to_html_node(
            "Here is ![alt](https://img.com/pic.png) an image."
        )
        self.assertEqual(
            result.to_html(),
            '<div><p>Here is <img src="https://img.com/pic.png" alt="alt"></img> an image.</p></div>',
        )

    def test_paragraph_multiline_joined_with_spaces(self):
        md = "Line one\nline two\nline three"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(), "<div><p>Line one line two line three</p></div>"
        )

    # --- Heading tests ---
    def test_h1(self):
        result = markdown_to_html_node("# Heading 1")
        self.assertEqual(result.to_html(), "<div><h1>Heading 1</h1></div>")

    def test_h2(self):
        result = markdown_to_html_node("## Heading 2")
        self.assertEqual(result.to_html(), "<div><h2>Heading 2</h2></div>")

    def test_h3(self):
        result = markdown_to_html_node("### Heading 3")
        self.assertEqual(result.to_html(), "<div><h3>Heading 3</h3></div>")

    def test_h4(self):
        result = markdown_to_html_node("#### Heading 4")
        self.assertEqual(result.to_html(), "<div><h4>Heading 4</h4></div>")

    def test_h5(self):
        result = markdown_to_html_node("##### Heading 5")
        self.assertEqual(result.to_html(), "<div><h5>Heading 5</h5></div>")

    def test_h6(self):
        result = markdown_to_html_node("###### Heading 6")
        self.assertEqual(result.to_html(), "<div><h6>Heading 6</h6></div>")

    def test_heading_with_inline_bold(self):
        result = markdown_to_html_node("## A **bold** heading")
        self.assertEqual(result.to_html(), "<div><h2>A <b>bold</b> heading</h2></div>")

    # --- Code block tests ---
    def test_code_block(self):
        md = "```\nprint('hello')\n```"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(), "<div><pre><code>print('hello')</code></pre></div>"
        )

    def test_code_block_multiline(self):
        md = "```\nline 1\nline 2\nline 3\n```"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><pre><code>line 1\nline 2\nline 3</code></pre></div>",
        )

    def test_code_block_no_inline_parsing(self):
        md = "```\nThis has **bold** and _italic_\n```"
        result = markdown_to_html_node(md)
        # Code blocks should NOT parse inline markdown
        self.assertEqual(
            result.to_html(),
            "<div><pre><code>This has **bold** and _italic_</code></pre></div>",
        )

    # --- Quote block tests ---
    def test_quote_single_line(self):
        md = "> This is a quote"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><blockquote>This is a quote</blockquote></div>",
        )

    def test_quote_multiple_lines(self):
        md = "> Line one\n> Line two\n> Line three"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><blockquote>Line one Line two Line three</blockquote></div>",
        )

    def test_quote_with_inline_bold(self):
        md = "> This is **bold** in a quote"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><blockquote>This is <b>bold</b> in a quote</blockquote></div>",
        )

    # --- Unordered list tests ---
    def test_unordered_list_single_item(self):
        md = "- Item one"
        result = markdown_to_html_node(md)
        self.assertEqual(result.to_html(), "<div><ul><li>Item one</li></ul></div>")

    def test_unordered_list_multiple_items(self):
        md = "- Item one\n- Item two\n- Item three"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><ul><li>Item one</li><li>Item two</li><li>Item three</li></ul></div>",
        )

    def test_unordered_list_with_inline_markdown(self):
        md = "- **Bold** item\n- _Italic_ item\n- `Code` item"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><ul><li><b>Bold</b> item</li><li><i>Italic</i> item</li><li><code>Code</code> item</li></ul></div>",
        )

    # --- Ordered list tests ---
    def test_ordered_list_single_item(self):
        md = "1. First item"
        result = markdown_to_html_node(md)
        self.assertEqual(result.to_html(), "<div><ol><li>First item</li></ol></div>")

    def test_ordered_list_multiple_items(self):
        md = "1. First\n2. Second\n3. Third"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><ol><li>First</li><li>Second</li><li>Third</li></ol></div>",
        )

    def test_ordered_list_with_inline_markdown(self):
        md = "1. **Bold** item\n2. _Italic_ item\n3. `Code` item"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><ol><li><b>Bold</b> item</li><li><i>Italic</i> item</li><li><code>Code</code> item</li></ol></div>",
        )

    # --- Multiple blocks tests ---
    def test_heading_and_paragraph(self):
        md = "# Title\n\nThis is a paragraph."
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><h1>Title</h1><p>This is a paragraph.</p></div>",
        )

    def test_multiple_block_types(self):
        md = "# Title\n\nA paragraph.\n\n- Item 1\n- Item 2"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><h1>Title</h1><p>A paragraph.</p><ul><li>Item 1</li><li>Item 2</li></ul></div>",
        )

    def test_full_document(self):
        md = "# My Doc\n\nA paragraph with **bold** text.\n\n> A quote\n\n```\nsome code\n```\n\n- Bullet one\n- Bullet two\n\n1. First\n2. Second"
        result = markdown_to_html_node(md)
        expected = (
            "<div>"
            "<h1>My Doc</h1>"
            "<p>A paragraph with <b>bold</b> text.</p>"
            "<blockquote>A quote</blockquote>"
            "<pre><code>some code</code></pre>"
            "<ul><li>Bullet one</li><li>Bullet two</li></ul>"
            "<ol><li>First</li><li>Second</li></ol>"
            "</div>"
        )
        self.assertEqual(result.to_html(), expected)

    def test_multiple_paragraphs(self):
        md = "First paragraph.\n\nSecond paragraph."
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><p>First paragraph.</p><p>Second paragraph.</p></div>",
        )

    def test_heading_paragraph_code(self):
        md = "## Subtitle\n\nSome text here.\n\n```\nx = 1\n```"
        result = markdown_to_html_node(md)
        self.assertEqual(
            result.to_html(),
            "<div><h2>Subtitle</h2><p>Some text here.</p><pre><code>x = 1</code></pre></div>",
        )


if __name__ == "__main__":
    unittest.main()

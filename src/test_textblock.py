import unittest

from textblock import markdown_to_blocks, block_to_blocktype, BlockType


class TestMarkdownToBlocks(unittest.TestCase):
    def test_single_block(self):
        result = markdown_to_blocks("This is a single block")
        self.assertEqual(result, ["This is a single block"])

    def test_multiple_blocks(self):
        md = "First block\n\nSecond block\n\nThird block"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["First block", "Second block", "Third block"])

    def test_strips_whitespace(self):
        md = "  leading space\n\ntrailing space  \n\n  both  "
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["leading space", "trailing space", "both"])

    def test_filters_empty_blocks(self):
        md = "first\n\n\n\nsecond"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["first", "second"])

    def test_many_blank_lines(self):
        md = "a\n\n\n\n\n\nb"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["a", "b"])

    def test_empty_string(self):
        result = markdown_to_blocks("")
        self.assertEqual(result, [])

    def test_only_whitespace(self):
        result = markdown_to_blocks("   \n\n   ")
        self.assertEqual(result, [])

    def test_only_newlines(self):
        result = markdown_to_blocks("\n\n\n\n")
        self.assertEqual(result, [])

    def test_multiline_block_preserved(self):
        md = "line one\nline two\nline three\n\nsecond block"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["line one\nline two\nline three", "second block"])

    def test_heading_and_paragraph(self):
        md = "# Heading\n\nThis is a paragraph."
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["# Heading", "This is a paragraph."])

    def test_heading_paragraph_and_list(self):
        md = "# Heading\n\nParagraph text.\n\n* item 1\n* item 2\n* item 3"
        result = markdown_to_blocks(md)
        self.assertEqual(
            result,
            ["# Heading", "Paragraph text.", "* item 1\n* item 2\n* item 3"],
        )

    def test_leading_trailing_blank_lines(self):
        md = "\n\nfirst\n\nsecond\n\n"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["first", "second"])

    def test_block_with_inline_markdown(self):
        md = "This has **bold** text\n\nThis has `code` text"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["This has **bold** text", "This has `code` text"])


class TestBlockToBlocktype(unittest.TestCase):
    # --- Heading tests ---
    def test_h1(self):
        self.assertEqual(block_to_blocktype("# Heading"), BlockType.HEADING)

    def test_h2(self):
        self.assertEqual(block_to_blocktype("## Heading 2"), BlockType.HEADING)

    def test_h3(self):
        self.assertEqual(block_to_blocktype("### Heading 3"), BlockType.HEADING)

    def test_h6(self):
        self.assertEqual(block_to_blocktype("###### Heading 6"), BlockType.HEADING)

    def test_heading_no_space_is_paragraph(self):
        self.assertEqual(block_to_blocktype("#NoSpace"), BlockType.PARAGRAPH)

    def test_heading_empty_text(self):
        self.assertEqual(block_to_blocktype("# "), BlockType.HEADING)

    # --- Code block tests ---
    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        self.assertEqual(block_to_blocktype(block), BlockType.CODE)

    def test_code_block_multiline(self):
        block = "```\nline 1\nline 2\nline 3\n```"
        self.assertEqual(block_to_blocktype(block), BlockType.CODE)

    def test_code_block_missing_closing(self):
        block = "```\nsome code"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_code_block_missing_opening(self):
        block = "some code\n```"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_code_block_no_newline_after_opening(self):
        block = "```code\n```"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_code_block_inline_backticks_not_code(self):
        block = "```hello```"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    # --- Quote block tests ---
    def test_quote_single_line(self):
        self.assertEqual(block_to_blocktype("> A quote"), BlockType.QUOTE)

    def test_quote_multiple_lines(self):
        block = "> Line 1\n> Line 2\n> Line 3"
        self.assertEqual(block_to_blocktype(block), BlockType.QUOTE)

    def test_quote_no_space_after_gt(self):
        self.assertEqual(block_to_blocktype(">NoSpace"), BlockType.QUOTE)

    def test_quote_empty_line(self):
        self.assertEqual(block_to_blocktype(">"), BlockType.QUOTE)

    def test_quote_mixed_missing_gt_is_paragraph(self):
        block = "> Line 1\nLine 2 without gt"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    # --- Unordered list tests ---
    def test_unordered_list_single_item(self):
        self.assertEqual(block_to_blocktype("- Item one"), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_blocktype(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_no_space_is_paragraph(self):
        self.assertEqual(block_to_blocktype("-NoSpace"), BlockType.PARAGRAPH)

    def test_unordered_list_missing_dash_is_paragraph(self):
        block = "- Item 1\nItem 2"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_unordered_list_empty_item(self):
        self.assertEqual(block_to_blocktype("- "), BlockType.UNORDERED_LIST)

    # --- Ordered list tests ---
    def test_ordered_list_single_item(self):
        self.assertEqual(block_to_blocktype("1. First item"), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        block = "1. First\n2. Second\n3. Third"
        self.assertEqual(block_to_blocktype(block), BlockType.ORDERED_LIST)

    def test_ordered_list_large_numbers(self):
        block = "10. Tenth\n11. Eleventh\n12. Twelfth"
        self.assertEqual(block_to_blocktype(block), BlockType.ORDERED_LIST)

    def test_ordered_list_no_space_is_paragraph(self):
        self.assertEqual(block_to_blocktype("1.NoSpace"), BlockType.PARAGRAPH)

    def test_ordered_list_missing_number_is_paragraph(self):
        block = "1. First\nSecond without number"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_ordered_list_letter_prefix_is_paragraph(self):
        self.assertEqual(block_to_blocktype("A. Item"), BlockType.PARAGRAPH)

    # --- Paragraph (default) tests ---
    def test_plain_text_is_paragraph(self):
        self.assertEqual(
            block_to_blocktype("Just some plain text"), BlockType.PARAGRAPH
        )

    def test_multiline_plain_text_is_paragraph(self):
        block = "Line one\nLine two\nLine three"
        self.assertEqual(block_to_blocktype(block), BlockType.PARAGRAPH)

    def test_text_with_inline_markdown_is_paragraph(self):
        self.assertEqual(
            block_to_blocktype("This has **bold** and *italic* text"),
            BlockType.PARAGRAPH,
        )

    def test_single_word_is_paragraph(self):
        self.assertEqual(block_to_blocktype("hello"), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()

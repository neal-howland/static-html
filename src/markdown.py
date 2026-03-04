from textblock import markdown_to_blocks, block_to_blocktype, BlockType
from textnode import TextNode, text_to_textnodes, TextType
from htmlnode import text_node_to_html_node, ParentNode, LeafNode
import re


def text_to_children(text):
    children = []
    textnodes = text_to_textnodes(text)
    for node in textnodes:
        children.append(text_node_to_html_node(node))

    return children


def extract_title(markdown):
    """
    Returns the first h1 ('# ') line from the markdown string
    """
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    raise Exception("No title header found.")


def markdown_to_html_node(markdown):
    """
    Converts a full markdown document into a single parent HTMLNode.
    That parent node will contain many child HTMLNode representing
    the nested elements.
    """

    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)

    nodes = []

    # Loop over each block
    for block in blocks:
        #   Determine the type of block
        block_type = block_to_blocktype(block)

        #   Based on the type of block, create a new HTMLNode with the proper data
        if block_type == BlockType.HEADING:
            nodes.append(
                ParentNode(
                    tag=f"h{block.count('#')}",
                    children=text_to_children(block.lstrip("#").strip()),
                )
            )

        #   The "code" block is a bit of a special case: it should not do any inline markdown parsing of its children. I didn't use my text_to_children function for this block type, I manually made a TextNode and used text_node_to_html_node.
        elif block_type == BlockType.CODE:
            node = TextNode(block.strip("```").strip(), TextType.CODE)
            p_node = ParentNode(tag="pre", children=[text_node_to_html_node(node)])
            nodes.append(p_node)

        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            stripped = " ".join(re.sub(r"^> ", "", line).strip() for line in lines)
            nodes.append(
                ParentNode(
                    tag="blockquote",
                    children=text_to_children(stripped),
                )
            )

        elif block_type == BlockType.UNORDERED_LIST:
            item_nodes = []
            text_items = block.split("\n")
            for item in text_items:
                item_nodes.append(
                    ParentNode(
                        tag="li", children=text_to_children(item.lstrip("- ").strip())
                    )
                )

            nodes.append(ParentNode(tag="ul", children=item_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            item_nodes = []

            text_items = block.split("\n")
            for item in text_items:
                item_nodes.append(
                    ParentNode(
                        tag="li",
                        children=text_to_children(
                            re.sub(r"^\d+\.\s", "", item).strip()
                        ),
                    )
                )

            nodes.append(ParentNode(tag="ol", children=item_nodes))

        elif block_type == BlockType.PARAGRAPH:
            nodes.append(
                ParentNode(
                    tag="p", children=text_to_children(re.sub(r"\n", " ", block))
                )
            )

    #   Assign the proper child HTMLNode objects to the block node. I created a shared text_to_children(text) function that works for all block types. It takes a string of text and resturns a list of HTMLNodes that represent the inline markdown using previously created function (think TextNode->HMTLNode)

    # Make all the block nodes children under a single parent HTML node (which should just be a div) and return it.
    return ParentNode(tag="div", children=nodes)

    # TIPS
    # Quote blocks should be surrounded by a <blockquote> tag
    # Unordered list block should be surrounded by a <ul> tag, and each list item should be surrounded by a <li> tag
    # Ordered list block should be surrounded by a <ol> tag, and each list item should be surrounde dby a <li> tag
    # Code blocks should be surrounded by a <code> tag nested inside a <pre> tag
    # Headings should be surrounded by a <h1> to <h6> tag, depending on the number of # characters
    # Paragraphs should be surrounded by a <p> tag. I removed the newlines and replaced them with spaces.

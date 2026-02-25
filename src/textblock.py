from enum import Enum
import re


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    raw_blocks = markdown.split("\n\n")
    blocks = []
    for block in raw_blocks:
        block = block.strip()
        if block != "":
            blocks.append(block)
    return blocks


def block_to_blocktype(block):
    if re.match(r"^#+\s", block):
        return BlockType.HEADING
    if re.match(r"^```\n[\s\S]+\n```$", block):
        return BlockType.CODE
    if re.match(r"^(>[^\n]*\n?)+$", block):
        return BlockType.QUOTE
    if re.match(r"^(- [^\n]*\n?)+$", block):
        return BlockType.UNORDERED_LIST
    if re.match(r"^(\d+\. [^\n]*\n?)+$", block):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

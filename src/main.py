import os
import shutil
import re
import sys

from markdown import markdown_to_html_node, extract_title


def generate_page(from_path, template_path, dest_path, basepath="/"):
    """
    Takes markdown source file from_path and generates html at dest_path using template_path as the template
    """

    print(f"Generating page from {from_path} to {dest_path} with {template_path}.")
    with open(from_path, "r") as f:
        markdown = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    content = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    html = re.sub(r"{{\s*Content\s*}}", content, template)
    html = re.sub(r"{{\s*Title\s*}}", title, html)
    html = re.sub(r'href="/', f'href="{basepath}', html)
    html = re.sub(r'src="/', f'src="{basepath}', html)

    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))

    with open(dest_path, "w") as f:
        f.write(html)


def generate_pages_recursive(
    dir_path_content, template_path, dest_dir_path, basepath="/"
):
    print(
        f"generate_pages_recursive({dir_path_content}, {template_path}, {dest_dir_path})"
    )
    if not os.path.exists(dir_path_content):
        raise Exception(f"Source path {dir_path_content} doesn't exist.")
    if os.path.isfile(dir_path_content):
        raise Exception(
            f"Source path {dir_path_content} is a file, expected a directory."
        )

    content_files = os.listdir(dir_path_content)

    for file in content_files:
        source = os.path.join(dir_path_content, file)
        print(f"  file: {file}")
        if os.path.isfile(source):
            print("    is a file")
            dest = os.path.join(dest_dir_path, re.sub(r"\.md$", ".html", file))
            generate_page(source, template_path, dest, basepath)
            continue
        else:
            print("    is a directory")
            dest = os.path.join(dest_dir_path, file)
            os.mkdir(dest)
            generate_pages_recursive(
                source,
                template_path,
                dest,
                basepath,
            )


def clean_copy(source, target, log_file=None):
    if os.path.exists(target):
        shutil.rmtree(target)

    os.mkdir(target)

    recursive_copy(source, target, log_file)


def recursive_copy(source, target, log_file=None):
    """
    Write a recursive function that copies all the contents from a source directory to a destination directory (in our case, static to public)
    It should first delete all the contents of the destination directory (public) to ensure that the copy is clean.
    It should copy all files and subdirectories, nested files, etc.
    I recommend logging the path of each file you copy, so you can see what's happening as you run and debug your code.
    """

    if not os.path.exists(source):
        raise Exception(f"Source '{source}' does not exist.")
    if os.path.isfile(source):
        raise Exception(f"Source '{source}' is a file, expected a directory.")

    for file in os.listdir(source):
        file_path = os.path.join(source, file)
        target_path = os.path.join(target, file)

        if os.path.isfile(file_path):
            shutil.copy(file_path, target_path)
            if log_file:
                with open(log_file, "a") as f:
                    f.write(f"Copied file: {file_path}\n")
                    f.write(f"         to: {target_path}\n")
        else:
            target_path = os.path.join(target, file)
            os.mkdir(target_path)
            recursive_copy(file_path, target_path, log_file)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    log_path = "logs"
    log_file = "static.log"

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    clean_copy("static", "public", os.path.join(log_path, log_file))
    generate_pages_recursive("content", "template.html", "public", basepath)


if __name__ == "__main__":
    main()

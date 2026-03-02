import os
import shutil


def clean_copy(source, target, log_file=None):
    print(f"==> clean_copy({source}, {target}, {log_file})")
    if os.path.exists(target):
        print(f"target path exists, deleting: {target}")
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

    print(f"==> recursive_copy({source}, {target}, {log_file})")
    if not os.path.exists(source):
        raise Exception(f"Source '{source}' does not exist.")
    if os.path.isfile(source):
        raise Exception(f"Source '{source}' is a file, expected a directory.")

    for file in os.listdir(source):
        file_path = os.path.join(source, file)
        target_path = os.path.join(target, file)

        if os.path.isfile(file_path):
            print(f"    file_path {file_path} is file.")
            print(f"    copying to {target_path}")
            shutil.copy(file_path, target_path)
            if log_file:
                with open(log_file, "a") as f:
                    f.write(f"Copied file: {file_path}\n")
                    f.write(f"         to: {target_path}\n")
        else:
            print(f"    file_path {file_path} is NOT file.")
            target_path = os.path.join(target, file)
            print(f"    mkdir target_path {target_path}")
            os.mkdir(target_path)
            recursive_copy(file_path, target_path, log_file)


def main():
    log_path = "logs"
    log_file = "static.log"

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    clean_copy("static", "public", os.path.join(log_path, log_file))


if __name__ == "__main__":
    main()

import os
import sys

# this script compares and
# yields statistics about
# VisIt-exported Curve2D
# lineouts


def parse_lineout(filepath: str) -> list:
    """
    Helper function to parse a lineout file.

        Parameters:
            filepath (str): the path to the file

        Returns:
            list: the parsed lineout data
    """

    # read the file
    with open(filepath, "r") as file:
        lines: list[str] = file.readlines()

    # parse the data
    # ignore the header
    # and split the data
    # to only get the
    # temperature values
    return [float(line.split(" ")[1]) for line in lines[3:]]


if __name__ == "__main__":
    # get both lineout folders
    # from console arguments
    if len(sys.argv) != 3:
        print(
            "Usage: python compare_lineouts.py <reference_folder> <comparison_folder>"
        )
        sys.exit(1)

    # get both folders
    reference_folder: str = sys.argv[1]
    comparison_folder: str = sys.argv[2]

    # check if they are valid
    # folders and exist
    if not os.path.exists(reference_folder) or not os.path.exists(comparison_folder):
        print("Error: folders do not exist")
        sys.exit(1)

    # load all files from
    # both folders
    reference_files = os.listdir(reference_folder)
    comparison_files = os.listdir(comparison_folder)

    # check if they have the same
    # number of files
    if len(reference_files) != len(comparison_files):
        print("Error: folders do not have the same number of files")
        sys.exit(1)

    # read and parse all files
    # into individual arrays
    reference_data = [
        parse_lineout(os.path.join(reference_folder, file)) for file in reference_files
    ]
    comparison_data = [
        parse_lineout(os.path.join(comparison_folder, file))
        for file in comparison_files
    ]

    # compute the mean and
    # standard deviation
    # for each file

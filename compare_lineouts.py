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
    # to get the keys and
    # temperature values
    return [
        (float(line.split(" ")[0]), float(line.split(" ")[1])) for line in lines[3:]
    ]


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
    reference_files: list = os.listdir(reference_folder)
    comparison_files: list = os.listdir(comparison_folder)

    # check if they have the same
    # number of files
    if len(reference_files) != len(comparison_files):
        print("Error: folders do not have the same number of files")
        sys.exit(1)

    # read and parse all files
    # into individual arrays
    reference_data: list = [
        parse_lineout(os.path.join(reference_folder, file)) for file in reference_files
    ]
    comparison_data: list = [
        parse_lineout(os.path.join(comparison_folder, file)) for file in comparison_files
    ]

    # compute the RMSE in [°C]
    # of the comparison data
    # with respect to the
    # reference data
    rmse: list[float] = [
        (
            sum([(r[1] - c[1]) ** 2 for r, c in zip(reference, comparison)])
            / len(reference)
        )
        ** 0.5
        for reference, comparison in zip(reference_data, comparison_data)
    ]

    # get the average and
    # standard deviation
    # of the RMSE
    average_rmse: float = sum(rmse) / len(rmse)
    std_rmse: float = (sum([(r - average_rmse) ** 2 for r in rmse]) / len(rmse)) ** 0.5

    # compute the relative error
    relative_errors: list = [
        sum(abs((r[1] - c[1]) / r[1]) * 100 for r, c in zip(reference, comparison))
        / len(reference)
        for reference, comparison in zip(reference_data, comparison_data)
    ]

    # get the average and
    # standard deviation
    # of the relative errors
    average_relative_error: float = sum(relative_errors) / len(relative_errors)
    std_relative_error: float = (
        sum([(r - average_relative_error) ** 2 for r in relative_errors])
        / len(relative_errors)
    ) ** 0.5

    # print the results
    print(f"Average RMSE: {average_rmse:.3f} [°C]")
    print(f"Standard Deviation of RMSE: {std_rmse:.3f} [°C]")
    print(f"Average Relative Error: {average_relative_error:.3f} [%]")
    print(f"Standard Deviation of Relative Error: {std_relative_error:.3f} [%]")

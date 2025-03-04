from typing import List
import pandas as pd
import os
import inquirer

INPUT_FILE_NAME = ""
OUTPUT_FILE_NAME = ""

## formatting
BOLD = "\033[1m"
ITALIC = "\033[3m"
RESET = "\033[0m"


def inquire(message: str, choices: List) -> str:
    """
    Prompt the user with a list of choices and return the selected choice.
    Args:
        message (str): The message to display to the user.
        choices (list): A list of choices for the user to select from.
    Returns:
        str: The choice selected by the user.
    """
    questions = [
        inquirer.List(
            "choice",
            message=message + " (use ↓ ↑ to navigate)",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    return answer["choice"]


def process_file(sheet, key_column: str, value_column: str) -> None:
    """
    Processes an Excel sheet and converts it into a PHP array format.
    Args:
        sheet (pandas.DataFrame): The Excel sheet to process.
        key_column (str): The column name to use as keys in the PHP array.
        value_column (str): The column name to use as values in the PHP array.
    Returns:
        None
    The function reads the specified columns from the given Excel sheet, processes the data,
    and generates a PHP file with the array representation of the data. The output PHP file
    is saved in the 'output' directory with a predefined name.
    """
    indent_level = 1
    php_output = "<?php\n\nreturn [\n"

    for index, row in sheet.iterrows():
        key = str(row[f"{key_column}"]).strip()
        value = str(row[f"{value_column}"]).strip()

        if key == "]" or key.strip() == "]" or key == "],":
            if indent_level > 1:
                indent_level -= 1
                php_output += f"{' ' * (indent_level * 4)}],\n"
            continue

        if "'" in key:
            key = key.replace("'", "")
        if "=>" in key:
            key = key.split("=>")[0].strip()

        if value == "nan" or not value:
            continue

        if value == "[" or value.strip() == "[":
            php_output += f"{' ' * (indent_level * 4)}'{key}' => [\n"
            indent_level += 1
            continue

        if value.startswith("'") and value.endswith("',"):
            value = value[1:-2]
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        if value.endswith("',"):
            value = value[:-2]
        if value.startswith("*'"):
            value = value[2:]
        if value.startswith("'"):
            value = value[1:]
        if value.endswith(","):
            value = value[:-1]

        value = value.replace("'", "\\'")

        php_output += f"{' ' * (indent_level * 4)}'{key}' => '{value}',\n"

    while indent_level > 1:
        indent_level -= 1
        php_output += f"{' ' * (indent_level * 4)}],\n"

    php_output += "];\n\nreturn $messages;\n?>"
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        with open(
            os.path.join(output_dir, f"{OUTPUT_FILE_NAME}.php"), "w", encoding="utf-8"
        ) as f:
            f.write(php_output)
        print(f"File stored as --> {OUTPUT_FILE_NAME}.php")
    except Exception as e:
        print(f"Expception occured: {e}")


if __name__ == "__main__":
    INPUT_FILE_NAME = input("Give your input file Name: ")
    if not os.path.isfile(INPUT_FILE_NAME):
        raise FileNotFoundError(
            f'Error opening "{INPUT_FILE_NAME}", check the file location and try again! '
        )

    excel_data = pd.ExcelFile(INPUT_FILE_NAME)

    final_sheet = inquire(
        f"{INPUT_FILE_NAME} has following sheets, select one to proceed",
        excel_data.sheet_names,
    )

    print(f"Selected sheet: {final_sheet}")

    parsed_sheet = excel_data.parse(f"{final_sheet}")
    key_column = inquire(
        f"'{final_sheet}' has following columns, select one as your {BOLD}KEY{RESET}",
        list(parsed_sheet.columns),
    )
    print(f"Selected {BOLD}Key column{RESET}: {key_column}")

    value_column = inquire(
        f"'{final_sheet} has following columns, select one as your {BOLD}VALUE{RESET} - {ITALIC}except {key_column}{RESET}",
        list(parsed_sheet.columns),
    )
    print(f"Selected {BOLD}Value column{RESET}: {value_column}")

    OUTPUT_FILE_NAME = input("Give output file name (without .php): ")

    process_file(parsed_sheet, key_column, value_column)

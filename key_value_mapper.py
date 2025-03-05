import os
import pandas as pd
from excel_to_php_converter import inquire, BOLD, ITALIC, RESET

INPUT_EXCEL_FILE = ""
INPUT_PHP_FILE = ""


def generate_modified_php_file(php_file_path, excel_data, php_data, base_name):
    """
    Generate a PHP file with the same structure as the input PHP file but with values updated
    according to the Excel sheet for matching keys.

    Args:
        php_file_path (str): Path to the original PHP file
        excel_data (dict): Dictionary containing Excel key-value pairs
        php_data (dict): Dictionary containing PHP key-value pairs
        base_name (str): Base name for the output file
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{base_name}_modified.php")

    with open(php_file_path, "r", encoding="utf-8") as f:
        php_content = f.readlines()

    modified_content = []
    nesting_stack = []
    current_path = []

    for line in php_content:
        modified_line = line
        line_strip = line.strip()

        if (
            "[" in line_strip
            and "=>" in line_strip
            and not line_strip.endswith(";")
            and "'" not in line_strip.split("=>")[1].strip()
        ):
            if line_strip.startswith("'") or line_strip.startswith('"'):
                parts = line_strip.split("=>")
                if len(parts) == 2:
                    key = parts[0].strip().strip("'\" ")
                    if current_path:
                        current_path.append(key)
                    else:
                        current_path = [key]
                    nesting_stack.append(key)

        elif line_strip == "]," or line_strip == "]":
            if current_path:
                current_path.pop()

        elif "=>" in line_strip and (
            line_strip.startswith("'") or line_strip.startswith('"')
        ):
            parts = line_strip.split("=>")
            if len(parts) == 2:
                key_part = parts[0].strip()
                key = key_part.strip("'\" ")

                if current_path:
                    full_key = ".".join(current_path + [key])
                else:
                    full_key = key

                if full_key in excel_data:
                    excel_value = excel_data[full_key]

                    value_part = parts[1].strip()

                    has_trailing_comma = value_part.endswith(",")

                    if "'" in value_part:
                        if has_trailing_comma:
                            modified_value = f"'{excel_value}',"
                        else:
                            modified_value = f"'{excel_value}'"
                    elif '"' in value_part:
                        if has_trailing_comma:
                            modified_value = f'"{excel_value}",'
                        else:
                            modified_value = f'"{excel_value}"'
                    else:
                        if has_trailing_comma:
                            modified_value = f"{excel_value},"
                        else:
                            modified_value = excel_value

                    modified_line = f"{key_part} => {modified_value}"

                    indent = line[: line.find(line.lstrip())]
                    modified_line = f"{indent}{modified_line}\n"

                    print(
                        f"Updating key: {full_key}, Old value: {value_part[:10]}, New value: {modified_value[:10]} -- stripped"
                    )

        modified_content.append(modified_line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(modified_content)

    print(f"Generated modified PHP file: {output_file}")
    print(
        f"Updated {BOLD}{len([k for k in excel_data.keys() if k in php_data])}{RESET} key-value pairs"
    )


def generate_new_keys_php_file(excel_data, php_data, base_name):
    """
    Generate a PHP file with the key-value pairs that exist in the Excel sheet but not in the PHP file.

    Args:
        excel_data (dict): Dictionary containing Excel key-value pairs
        php_data (dict): Dictionary containing PHP key-value pairs
        base_name (str): Base name for the output file
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{base_name}_new_keys.php")

    missing_keys = {k: v for k, v in excel_data.items() if k not in php_data}

    grouped_keys = {}
    for key, value in missing_keys.items():
        parts = key.split(".")

        if len(parts) > 1:
            parent_key = ".".join(parts[:-1])
            child_key = parts[-1]

            if parent_key not in grouped_keys:
                grouped_keys[parent_key] = {}

            grouped_keys[parent_key][child_key] = value
        else:
            if "root" not in grouped_keys:
                grouped_keys["root"] = {}
            grouped_keys["root"][key] = value

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<?php\n\nreturn [\n")

        if "root" in grouped_keys:
            for key, value in grouped_keys["root"].items():
                f.write(f"    '{key}' => '{value}',\n")

        for parent_key, children in grouped_keys.items():
            if parent_key != "root":
                parent_parts = parent_key.split(".")

                indent = "    "
                f.write(f"{indent}'{parent_parts[0]}' => [\n")
                indent += "    "

                for i in range(1, len(parent_parts)):
                    f.write(f"{indent}'{parent_parts[i]}' => [\n")
                    indent += "    "

                for key, value in children.items():
                    f.write(f"{indent}'{key}' => '{value}',\n")

                for i in range(len(parent_parts)):
                    indent = indent[:-4]
                    f.write(f"{indent}],\n")

        f.write("];\n")

    print(f"Generated new keys PHP file: {output_file}")


def export_key_value_pairs(excel_data, php_data, base_name):
    """
    Export key-value pairs from both data sources to text files for manual comparison.

    Args:
        excel_data (dict): Dictionary containing Excel key-value pairs
        php_data (dict): Dictionary containing PHP key-value pairs
        base_name (str): Base name for the output files
    """
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)

    excel_file = os.path.join(output_dir, f"{base_name}_excel_pairs.txt")
    with open(excel_file, "w", encoding="utf-8") as f:
        f.write("Excel Key-Value Pairs\n")
        f.write("=" * 60 + "\n\n")

        for key in sorted(excel_data.keys()):
            value = excel_data[key]
            f.write(f"'{key}' => '{value}'\n")

    php_file = os.path.join(output_dir, f"{base_name}_php_pairs.txt")
    with open(php_file, "w", encoding="utf-8") as f:
        f.write("PHP Key-Value Pairs\n")
        f.write("=" * 60 + "\n\n")

        for key in sorted(php_data.keys()):
            value = php_data[key]
            f.write(f"'{key}' => '{value}'\n")

    modified_file = os.path.join(output_dir, f"{base_name}_potential_modified.txt")
    with open(modified_file, "w", encoding="utf-8") as f:
        f.write("Potential Modified Values (Keys in both files)\n")
        f.write("=" * 60 + "\n\n")

        common_keys = set(excel_data.keys()) & set(php_data.keys())

        for key in sorted(common_keys):
            excel_value = excel_data[key]
            php_value = php_data[key]
            f.write(f"Key: '{key}'\n")
            f.write(f"  Excel: '{excel_value}'\n")
            f.write(f"  PHP:   '{php_value}'\n")
            f.write(f"  Same?  {excel_value == php_value}\n")
            f.write("\n")

    print(
        f"\nExported key-value pairs to {ITALIC}'{output_dir}'{RESET} directory for manual comparison"
    )
    print(f"- Excel pairs: {excel_file}")
    print(f"- PHP pairs: {php_file}")
    print(f"- Potential modified values: {modified_file}")


def process_file(sheet, key_column, value_column, php_file_path):
    """
    Compare key-value pairs between an Excel sheet and a PHP file.
    Generate a report of differences focusing on keys missing in PHP and modified values.

    Args:
        sheet (pandas.DataFrame): The Excel sheet containing data
        key_column (str): The column name to use as keys
        value_column (str): The column name to use as values
        php_file_path (str): Path to the PHP file for comparison
    """
    excel_data = {}
    current_path = []

    debug_nested_keys = []

    for index, row in sheet.iterrows():
        key = str(row[key_column]).strip()
        value = str(row[value_column]).strip()

        if not key or key == "nan" or key == "":
            current_path = []
            continue

        if "'" in key:
            key = key.replace("'", "")
        if "=>" in key:
            key = key.split("=>")[0].strip()

        if value == "[" or value.strip() == "[":
            current_path.append(key)
            debug_nested_keys.append(".".join(current_path))
            continue

        if (value == "nan" or not value or value == "") and value != "[":
            continue

        value = clean_value(value)

        if current_path:
            full_key = ".".join(current_path + [key])
        else:
            full_key = key

        excel_data[full_key] = value

    print(f"\nExtracted {ITALIC}{len(excel_data)}{RESET} keys from Excel sheet")
    # print(f"Detected {len(debug_nested_keys)} nested keys: {debug_nested_keys[:5]}...") # no need

    php_data = extract_php_key_values(php_file_path)
    print(f"Extracted {ITALIC}{len(php_data)}{RESET} keys from PHP file")

    base_name = os.path.basename(php_file_path).replace(".php", "")
    export_key_value_pairs(excel_data, php_data, base_name)

    missing_in_php = []
    modified_values = []

    for key, excel_value in excel_data.items():
        if key not in php_data:
            missing_in_php.append((key, excel_value))
        else:
            php_value = php_data[key]
            excel_value_norm = normalize_value(excel_value)
            php_value_norm = normalize_value(php_value)

            if excel_value_norm != php_value_norm:
                modified_values.append((key, excel_value, php_value))

    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(
        output_dir,
        f"comparison_report_{key_column}_{value_column}_{os.path.basename(php_file_path).replace('.php', '')}.txt",
    )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Comparison Report: Excel vs PHP File\n")
        f.write(f"Excel File: {INPUT_EXCEL_FILE}, Sheet: {final_sheet}\n")
        f.write(f"PHP File: {php_file_path}\n")
        f.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"1. Keys in Excel but missing in PHP ({len(missing_in_php)})\n")
        f.write("-" * 60 + "\n")
        for key, value in missing_in_php:
            f.write(f"Key: '{key}' => '{value}'\n")
        f.write("\n")

        f.write(f"2. Keys with modified values ({len(modified_values)})\n")
        f.write("-" * 60 + "\n")
        for key, excel_value, php_value in modified_values:
            f.write(f"Key: '{key}'\n")
            f.write(f"  Excel value: '{excel_value}'\n")
            f.write(f"  PHP value:   '{php_value}'\n")
            f.write("\n")

    print(f"Comparison report generated: {report_file}")

    print("\nSUMMARY:")
    print(f"- Keys in Excel but missing in PHP: {BOLD}{len(missing_in_php)}{RESET}")
    print(f"- Keys with modified values: {BOLD}{len(modified_values)}{RESET}")

    base_name = os.path.basename(php_file_path).replace(".php", "")

    generate_modified_php_file(php_file_path, excel_data, php_data, base_name)

    generate_new_keys_php_file(excel_data, php_data, base_name)


def normalize_value(value):
    """
    Normalize a value for more accurate comparison.

    Args:
        value (str): The value to normalize

    Returns:
        str: Normalized value
    """
    value = str(value)

    value = " ".join(value.split())

    value = value.replace("'", "").replace('"', "")

    value = value.replace(".", "").replace(",", "")

    value = value.lower()

    return value


def clean_value(value):
    """Helper function to clean up value strings"""
    if value.startswith("'") and value.endswith("',"):
        value = value[1:-2]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    elif value.endswith("',"):
        value = value[:-2]
    elif value.startswith("*'"):
        value = value[2:]
    elif value.startswith("'"):
        value = value[1:]
    elif value.endswith(","):
        value = value[:-1]
    return value


def extract_php_key_values(php_file_path):
    """
    Extract key-value pairs from a PHP file with nested structure support.

    Args:
        php_file_path (str): Path to the PHP file

    Returns:
        dict: Dictionary containing key-value pairs from the PHP file
    """
    php_data = {}
    current_path = []
    current_nested_dict = php_data
    stack = []

    with open(php_file_path, "r", encoding="utf-8") as f:
        php_content = f.read()

    lines = php_content.split("\n")
    for line in lines:
        line = line.strip()

        if "=>" in line and "[" in line and line.endswith("["):
            if line.startswith("'") or line.startswith('"'):
                parts = line.split("=>")
                if len(parts) == 2:
                    key = parts[0].strip().strip("'\" ")

                    if current_path:
                        nested_dict = php_data
                        for parent_key in current_path:
                            if parent_key not in nested_dict:
                                nested_dict[parent_key] = {}
                            nested_dict = nested_dict[parent_key]

                        nested_dict[key] = {}
                        stack.append((current_path[:], current_nested_dict))
                        current_path.append(key)
                        current_nested_dict = nested_dict[key]
                    else:
                        php_data[key] = {}
                        stack.append((current_path[:], current_nested_dict))
                        current_path.append(key)
                        current_nested_dict = php_data[key]

        elif line == "]," or line == "]":
            if stack:
                current_path, current_nested_dict = stack.pop()

        elif "=>" in line and (line.startswith("'") or line.startswith('"')):
            parts = line.split("=>")
            if len(parts) == 2:
                key_part = parts[0].strip()
                value_part = parts[1].strip()

                key = key_part.strip("'\" ")

                value = value_part.strip()
                if value.startswith("'") and value.endswith("',"):
                    value = value[1:-2]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.startswith('"') and value.endswith('",'):
                    value = value[1:-2]
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.endswith(","):
                    value = value[:-1]

                if current_path:
                    nested_dict = php_data
                    for parent_key in current_path:
                        if parent_key not in nested_dict:
                            nested_dict[parent_key] = {}
                        nested_dict = nested_dict[parent_key]
                    nested_dict[key] = value
                else:
                    php_data[key] = value

    flattened_php = flatten_dict(php_data)
    return flattened_php


def flatten_dict(nested_dict, parent_key="", separator="."):
    """
    Flatten a nested dictionary structure into a single-level dictionary.

    Args:
        nested_dict (dict): The nested dictionary to flatten
        parent_key (str): The parent key for the current recursion level
        separator (str): Character to use to separate nested keys

    Returns:
        dict: Flattened dictionary with dot-notation keys
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


if __name__ == "__main__":
    INPUT_EXCEL_FILE = input(f"Give your input {BOLD}excel file Name{RESET}: ")

    if not os.path.isfile(INPUT_EXCEL_FILE):
        raise FileNotFoundError(
            f'Error opening "{INPUT_EXCEL_FILE}", check the file location or name and try again! '
        )
    excel_data = pd.ExcelFile(INPUT_EXCEL_FILE)

    final_sheet = inquire(
        f"{INPUT_EXCEL_FILE} has following sheets, select one to proceed",
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

    INPUT_PHP_FILE = input(f"Give your input {BOLD}PHP file Name{RESET}: ")
    if not os.path.isfile(INPUT_PHP_FILE):
        raise FileNotFoundError(
            f'Error opening "{INPUT_PHP_FILE}", check the file location or name and try again! '
        )

    # print(
    #     f"Given {INPUT_PHP_FILE} PHP file will be mapped with KEY: {key_column} & value: {value_column} of {parsed_sheet} sheet"
    # )

    process_file(parsed_sheet, key_column, value_column, INPUT_PHP_FILE)

import ast
from datetime import datetime as dt
from os import makedirs, path
from pandas import DataFrame as df, notnull, read_excel


def SaveAsExcel(
    data: list,
    flatten: bool = False,
    output: str = None,
    directory: str = "~",
    fileName: str = "PANBA_EXPORT",
    timestamp: bool = True,
) -> str:
    """Saving a bunch of data in Dictionary to excel. More or so is like '.to_excel()' method of pandas dataframe

    Args:
        data (list): List of data to be saved
        flatten (bool, optional): Should the data be Flatten?. Defaults to False.
        directory (str, optional): Directory of which the file will be reside. Defaults to "~".
        fileName (str, optional): What should the file called?. Defaults to "PANBA_EXPORT".
        timestamp (bool, optional): Should the naming of file including timestamp?. Defaults to True.

    Returns:
        str: Where the file saved
    """
    fileName = (
        f"{dt.now().strftime('%Y%m%d_%H%M%S')} - {fileName}" if timestamp else fileName
    )
    fileLoc = f"{directory}/{fileName}.xlsx" if output is None else output
    makedirs(path.dirname(fileLoc), exist_ok=True)
    data = [flatten_dict(data=row, level=1) for row in data] if flatten else data
    df(data=data).to_excel(excel_writer=fileLoc, index=False, header=True)
    return fileLoc


def flatten_dict(
    data: list, parent_key: str = "", sep: str = "_", level: int = 1
) -> dict:
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key != "" else key
        if isinstance(value, dict) and level > 0:
            items.extend(
                flatten_dict(data=value, parent_key=new_key, level=level - 1).items()
            )
        else:
            items.append((new_key, value))
    return dict(items)


def ReadFromExcel(file_loc: str) -> dict:
    from numpy import nan

    raw = read_excel(file_loc, dtype={"name": str})
    res = convert_json_columns(data=raw)
    res = res.replace(nan, None)
    return res.to_dict(orient="records")


def is_json_like(value):
    """
    Checks if a value is a JSON-like string by trying to safely evaluate it.
    Returns True if the value can be safely converted to a dict or list.
    """
    if not isinstance(value, str):
        return False
    try:
        parsed = ast.literal_eval(value)
        return isinstance(parsed, (dict, list))
    except (ValueError, SyntaxError):
        return False


def safe_literal_eval(value):
    """
    Safely evaluates a string using ast.literal_eval.
    If evaluation fails, it returns the original value.
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def convert_json_columns(data: df):
    """
    Detects columns with JSON-like strings and converts them into actual dictionaries or lists.
    """
    for column in data.columns:
        # Check if at least 50% of the non-null entries in the column are JSON-like
        non_null_values = data[column].dropna()
        json_like_count = non_null_values.apply(is_json_like).sum()
        if len(non_null_values) > 0 and (json_like_count / len(non_null_values)) >= 0.5:
            # Convert the column using safe_literal_eval
            data[column] = data[column].apply(safe_literal_eval)
    return data

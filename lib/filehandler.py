from datetime import datetime as dt
from os import makedirs, path
from pandas import DataFrame as df, read_excel


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
    res = read_excel(file_loc)
    return res.to_dict(orient="records")

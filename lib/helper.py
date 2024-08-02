def split_list(data: list, iter: int) -> list[any]:
    from numpy import array_split, array

    dataAsArray = array(data)
    chunked = array_split(dataAsArray, 4)
    res = [list(arr) for arr in chunked]
    return res


from rich.progress import Progress, TaskID  # noqa: E402
from itertools import chain  # noqa: E402


def split_task_with_progress(data: list, env: dict) -> dict:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from rich.console import Console

    errConsole = Console(stderr=True)
    with Progress(expand=True) as prog:
        overall = prog.add_task("Overall Progress", total=len(data))
        task_prog = []
        errList = []
        res: list = []
        with ThreadPoolExecutor() as exec:
            futures = []
            for i in range(len(data)):
                taskId: TaskID = prog.add_task(f"Worker {i}", total=len(data[i]) + 1)
                task_prog.append(taskId)
                futures.append(
                    exec.submit(
                        class_wrapper,
                        data[i],
                        env["bearerToken"],
                        prog,
                        taskId,
                        overall,
                    )
                )
            for future in as_completed(futures):
                res.append(future.result()["res"])
                errList.append(future.result()["error"])
    allRes = {
        "res": list(chain.from_iterable(res)),
        "err": errList if errList is not None else None,
    }
    return allRes


def class_wrapper(
    data: list,
    bearer: str,
    progress: Progress,
    taskId: TaskID,
    overallTaskId: TaskID,
) -> dict:
    from lib.api.getlist import InterfaceOfTenant as IoT

    res: list = []
    errList: dict = {}
    sliceLength = len(data)
    for row in data:
        progress.update(task_id=taskId, description=row["name"])
        try:
            task = IoT(bearerToken=bearer, siteId=row["site_id"], elementId=row["id"])
        except Exception as err:
            errList[row["name"]] = err
        for each in task.data["items"]:
            each.update(
                {
                    "site_name": row["name"],
                    "site_id": row["site_id"],
                    "element_id": row["id"],
                }
            )
        res.append(task.data["items"])
        progress.advance(task_id=taskId, advance=1)
        progress.advance(task_id=overallTaskId, advance=1 / sliceLength)
    progress.update(task_id=taskId, description="Flattening Result")
    progress.advance(task_id=taskId, advance=1)
    compRes = {}
    compRes["res"] = list(chain.from_iterable(res))
    compRes.update(error=errList)
    return compRes

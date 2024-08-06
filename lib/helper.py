def split_list(data: list, iter: int) -> list[any]:
    from numpy import array_split, array

    dataAsArray = array(data)
    chunked = array_split(dataAsArray, 4)
    res = [list(arr) for arr in chunked]
    return res


from rich.progress import Progress, TaskID  # noqa: E402
from itertools import chain  # noqa: E402


# [x]: Refactor for the sake of reusability
# HACK: This is not refactor per se, but working nonetheless
def split_task_with_progress(data: list, env: dict, fun) -> dict:
    from concurrent.futures import ThreadPoolExecutor, as_completed

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
                        fun,
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


def get_interface(
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
            task = IoT(
                bearerToken=bearer, siteId=row["site_id"], elementId=row["id"]
            ).get()
        except Exception as err:
            errList[row["name"]] = err
        # [x]: Site data details at the first of dictionary!
        for each in task["items"]:
            temp = {
                "site_name": row["name"],
                "site_id": row["site_id"],
                "element_id": row["id"],
            }
            temp.update(each)
            res.append(temp)
            del temp
        progress.advance(task_id=taskId, advance=1)
        progress.advance(task_id=overallTaskId, advance=1 / sliceLength)
    progress.update(task_id=taskId, description="Flattening Result")
    progress.advance(task_id=taskId, advance=1)
    compRes = {}
    compRes["res"] = res
    compRes.update(error=errList)
    return compRes


def put_interface(
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
        body = row
        [body.pop(key) for key in ["site_name", "site_id", "element_id"]]
        try:
            task = IoT(
                bearerToken=bearer, siteId=row["site_id"], elementId=row["element_id"]
            ).put(interfaceId=row["id"], body=body)
        except Exception as err:
            errList[row["name"]] = err
        res = {row["site_name"]: "success"}
        del body
        progress.advance(task_id=taskId, advance=1)
        progress.advance(task_id=overallTaskId, advance=1 / sliceLength)
    progress.update(task_id=taskId, description="Flattening Result")
    progress.advance(task_id=taskId, advance=1)
    compRes = {}
    compRes["res"] = res
    compRes.update(error=errList)
    return compRes

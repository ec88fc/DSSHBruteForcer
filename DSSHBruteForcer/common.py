import linecache
import json
import os


def File2ListByLine(path):
    fp = open(path)
    ret = []

    for line in fp.readlines():
        ret.append(line.strip())
    return ret


def FileTotalCounts(path):
    return len(["" for line in open(path, "r")])


def GetFileRangeLines(path, startIdx, endIdx):
    idx = startIdx
    ret = []
    while idx < endIdx:
        ret.append(linecache.getline(path, idx).strip())
        idx = idx + 1
    return ret


def GetJsonFileConfig(path):
    with open(path, "r") as load_f:
        ret = json.load(load_f)
        return ret


def Mkdir(path):
    if os.path.exists(path):
        return
    os.mkdir(path)

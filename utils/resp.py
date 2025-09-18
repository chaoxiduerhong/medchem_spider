# coding: utf-8
# Desc: response used functions

import json
from flask import request


def merge_params(dict1, dict2, dict3):
    merged_dict = {}
    all_keys = set(dict1.keys()) | set(dict2.keys()) | set(dict3.keys())
    for key in all_keys:
        if key in dict3 and dict3[key] is not None and dict3[key]:
            merged_dict[key] = dict3[key]
        elif key in dict2 and dict2[key] is not None and dict2[key]:
            merged_dict[key] = dict2[key]
        elif key in dict1 and dict1[key] is not None and dict1[key]:
            merged_dict[key] = dict1[key]
        else:
            merged_dict[key] = None
    return merged_dict


def form_input(field=None, default=None):
    """
    获取参数顺序，以json body为主，如果json body不存在，则获取url传递的参数
    :param field: 参数字段
    :param default: 返回的默认值
    :return:
    """
    # 获取表单传值

    formParams = request.get_data()
    try:
        if formParams:
            formParams = json.loads(formParams.decode("utf-8"))
        else:
            formParams = {}
    except:
        formParams = {}

    # 获取url传值
    urlParams = request.values.to_dict()

    # 获取json传值。如果是这里获取传值，必须传递的content-type:application/json 否则会报错
    try:
        jsonParams = request.json
    except:
        jsonParams = {}
    resData = merge_params(formParams, jsonParams, urlParams)
    if field == "*":
        return resData
    if field in resData:
        return resData[field]
    return default


def success(data=None, msg="request success"):
    return {
        "data": data,
        "msg": msg,
        "code": 200,
    }


def success_page(data):
    return data


def node_page(data=None, msg="request success"):
    return {
        "data": {
            "pages": {
                "children": data
            }
        },
        "status": 0,
        "msg": msg,
        "code": 200,
    }


def error(code, msg="request error", data=None):
    return {
        "data": data,
        "msg": msg,
        "code": code,
    }


def error_dict(code, msg="request error", data=None):
    return {
        "data": data,
        "msg": msg,
        "code": code,
        "info": msg,
    }


def field_filter(data, filed_list=None):
    if filed_list is None:
        return data
    if isinstance(data, list):
        result = []
        for item in data:
            item2 = item.copy()
            for key in item:
                if key in filed_list:
                    item2.pop(key)
            result.append(item2)
        return result
    else:
        data2 = data.copy()
        for key in data:
            if key in filed_list:
                data2.pop(key)
        return data2


def page_list(data, total, start=0, length=10, msg=''):
    return success({
        "total": total,
        "list": data,
        "start": start,
        "len": length,
    }, msg=msg)

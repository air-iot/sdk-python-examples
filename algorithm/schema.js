[
    {
        "title": "函数1-加法",
        "function": "add",
        "input": {
            "type": "object",
            "properties": {
                "num1": {
                    "title": "参数1",
                    "type": "number"
                },
                "num2": {
                    "title": "参数2",
                    "type": "number"
                }
            },
            "required": [
                "num1",
                "num2"
            ]
        },
        "output": {
            "type": "object",
            "properties": {
                "num1": {
                    "title": "结果",
                    "type": "number"
                }
            }
        }
    },
    {
        "title": "函数2-绝对值",
        "function": "abs",
        "input": {
            "type": "object",
            "properties": {
                "num1": {
                    "title": "参数1",
                    "type": "number"
                }
            },
            "required": [
                "num1"
            ]
        },
        "output": {
            "type": "object",
            "properties": {
                "res": {
                    "title": "结果",
                    "type": "number"
                }
            }
        }
    },
    {
        "title": "函数3-获取当前系统时间",
        "function": "now",
        "input": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "output": {
            "type": "object",
            "properties": {
                "sysdate": {
                    "title": "当前系统时间",
                    "type": "string"
                }
            }
        }
    },
    {
        "title": "函数4-数组参数",
        "function": "arrayArguments",
        "input": {
            "type": "object",
            "properties": {
                "arr1": {
                    "type": "array",
                    "title": "数组1",
                    "items": {
                        "type": "number"
                    }
                },
                "arr2": {
                    "type": "array",
                    "title": "数组2",
                    "items": {
                        "type": "number"
                    }
                }
            },
            "required": ["arr1", "arr2"]
        },
        "output": {
            "type": "object",
            "properties": {
                "result": {
                    "title": "结果",
                    "type": "number"
                }
            }
        }
    }
]
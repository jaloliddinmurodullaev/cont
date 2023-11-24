def logger(log):
    import requests
    import os
    import copy
    import ast
    import pickle
    func = log['func'] if log.get("func", False) else "logs_all"
    mes = ""
    Rlog = []

    try:
        with open(func, "rb") as fp:   
            Rlog = pickle.load(fp)
        os.remove(func)
        Rlog.append(f'{log}')
    except Exception as e:
        Rlog.append(f'{log}')

    heads = {
        "Content-Type": "application/json"
    }

    b = copy.copy(Rlog)
    try:
        success = []
        for c in Rlog:
            j = ast.literal_eval(c)
            res = requests.post('http://176.99.12.64:8081/api/log/add/', headers=heads, json=j)
            JRes = res.json()
            success.append({"type": JRes['type'], "uid": JRes['uid'], "func": JRes['func']})
            b.remove(c)
        mes = {"status":"success", "success": success}
    except Exception as e:
        d = copy.copy(b)
        with open(func, "wb") as fp:   
            pickle.dump(d, fp)

        mes = {"status":"error", "error": e, "message": "server error data save to file"}

    return mes


log = {
    "func": "logs_auth",
    "login": "rodnoc",
    "password": "asdasdasd",
    "user_ip": "111.111.111.111",
    "user_agent": "bot",
    "is_success": 'false'
}


print(logger(log))

log = {
    "func": "logs_errors",
    "user_id": "k4k5k3m2k77",
    "system": "logs",
    "module": "auth",
    "action": "bot",
    "error_code": "54546",
    "message": "Sintex error",
    "user_ip": "127.0.0.1",
    "user_agent": "Mazzilla",
    "referal_url": "http://b2b.site.ru/most"
}


print(logger(log))

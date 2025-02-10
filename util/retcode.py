class RETCODE:
    class CODE:
        code: int
        errmsg: str
        def __init__(self, code, errmsg):
            self.code = code
            self.errmsg = errmsg

    OK = CODE(200, 'OK')

def exception_handler(fun):

    def handler(self, *args):

        try:
            fun(self, *args)
        except FileNotFoundError as exc:
            self.status = 'failed'
            print("FileNotFoundError: {}".format(exc))

    return handler

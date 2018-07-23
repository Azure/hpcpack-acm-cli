
class Arguments:
    # Parameters:
    # args is the result of argparse.ArgumentParser#parse_args
    # config is configparser.ConfigParser()
    def __init__(self, args, config):
        self.args = args
        self.config = config

    def __getattr__(self, name):
        try:
            value = getattr(self.args, name)
        except AttributeError:
            raise
        if value is None:
            value = self.config.get('DEFAULT', name, fallback=None)
        return value

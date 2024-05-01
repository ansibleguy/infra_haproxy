class FilterModule(object):

    def filters(self):
        return {
            "ensure_list": self.ensure_list,
            "is_string": self.is_string,
        }

    @staticmethod
    def ensure_list(data: (str, list)) -> list:
        # if user supplied a string instead of a list => convert it to match our expectations
        if isinstance(data, list):
            return data

        return [data]

    @staticmethod
    def is_string(data) -> bool:
        return isinstance(data, str)

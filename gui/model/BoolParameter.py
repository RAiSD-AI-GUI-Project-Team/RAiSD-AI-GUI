from model.Parameter import Parameter

class BoolParameter(Parameter[bool]):
    def get_flag_with_value(self) -> str:
        if self.value:
            return self.flag
        else:
            return ""
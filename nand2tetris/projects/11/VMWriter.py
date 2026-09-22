class VMWriter:
    def __init__(self, output_file):
        self.output_file = output_file

    def write_push(self, segment, index):
        self.output_file.write(f"push {segment} {index}\n")

    def write_pop(self, segment, index):
        self.output_file.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command):
        self.output_file.write(f"{command}\n")

    def write_label(self, label):
        self.output_file.write(f"label {label}\n")

    def write_goto(self, label):
        self.output_file.write(f"goto {label}\n")

    def write_if(self, label):
        self.output_file.write(f"if-goto {label}\n")

    def write_call(self, name, argument_count):
        self.output_file.write(f"call {name} {argument_count}\n")

    def write_function(self, name, local_count):
        self.output_file.write(f"function {name} {local_count}\n")

    def write_return(self):
        self.output_file.write("return\n")

    def close(self):
        self.output_file.close()

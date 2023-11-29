import simple_data_flow as sdf
from simple_data_flow import dpg

class NewNode(sdf.Node):

    @staticmethod
    def factory(name, data):
        node = NewNode(name, data)
        return node

    def __init__(self, label: str, data):
        super().__init__(label, data)

        # add input attributes
        self.add_input_attribute(sdf.InputNodeAttribute("input"))

        # add output attributes
        self.add_output_attribute(sdf.OutputNodeAttribute("output"))

    def execute(self):

        # input data
        input_data_1 = self._input_attributes[0].get_data()

        # perform operations
        max_value = input_data_1[0]
        for value in input_data_1:
            if value > max_value:
                max_value = value

        # call execute on output attributes with data
        self._output_attributes[0].execute(max_value)

        # call finish
        self.finish()


app = sdf.App()

app.add_inspector("New Inspector", NewNode.factory)

app.start()

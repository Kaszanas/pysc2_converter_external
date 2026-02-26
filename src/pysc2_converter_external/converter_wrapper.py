class ConverterWrapper:
    def __init__(self, converter):
        self.converter = converter

    def observation_spec(self):

        return_observation_spec = self.converter.observation_spec()

        return return_observation_spec

    def action_spec(self):

        return_action_spec = self.converter.action_spec()

        return return_action_spec

    def convert_observation(self, observation):

        converted_observation = self.converter.convert_observation(observation)

        return converted_observation

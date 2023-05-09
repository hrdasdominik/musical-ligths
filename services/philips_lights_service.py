from typing import List
from repositories.philips_lights_api import PhilipsLightsApi
from models.philips_light_model import PhilipsLightModel


class PhilipsLightsService:
    """_summary_"""

    def __init__(self, lights_api: PhilipsLightsApi) -> None:
        self.lights_api = lights_api

    def turn_on_all_lights(self):
        lights: List[PhilipsLightModel] = self.lights_api.get_all_lights()
        for light in lights:
            light.state.on = True
            self.lights_api.send_data_change(light)
    
    def turn_off_all_lights(self):
        lights: List[PhilipsLightModel] = self.lights_api.get_all_lights()
        for light in lights:
            light.state.on = False
            self.lights_api.send_data_change(light)


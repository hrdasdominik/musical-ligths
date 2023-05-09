import json
from typing import List
import requests
from utils.decorators import *

from repositories.philips_base_api import PhilipsBaseApi
from models.philips_light_model import *

from utils.logger import logging


class PhilipsLightsApi(PhilipsBaseApi):
    """_summary_"""

    def __init__(self) -> None:
        super().__init__()

    @get("/lights")
    def get_all_lights(self, endpoint: str) -> List[PhilipsLightModel] | None:
        return self.get_data(endpoint)

    @get("/lights/{id}")
    def get_a_light(self, endpoint: str, id: int) -> PhilipsLightModel | None:
        return self.get_data(endpoint, id)

    @get("/lights/{id}/state")
    def get_ligth_state(self, endpoint: str, id: int) -> State | None:
        return self.get_data(endpoint, id)
    
    @put()
    def send_data_change(self, endpoint, light: PhilipsLightModel) -> None:
        if light is None:
            raise ValueError("Light object is None")
        light_id = light.id
        data = self.serialize_object(light)

        logging.info("PACKET REQUEST:", data)

        response = requests.put(
            super().get_base_url() + endpoint + f"/{light_id}", data
        )

        if response.status_code == requests.codes.ok and "error" not in str(
            response.content
        ):
            logging.info(
                str(response.status_code)
                + ", "
                + response.reason
                + " | "
                + str(response.content)
            )
        elif response.status_code != requests.codes.ok:
            logging.error(
                str(response.status_code)
                + ", "
                + response.reason
                + " | "
                + str(response.content)
            )
        else:
            logging.error(str(response.text))

    def serialize_object(self, light: PhilipsLightModel) -> json:
        data = light.__dict__
        del data["id"]
        data["state"] = data["state"].__dict__
        data["swupdate"] = data["swupdate"].__dict__
        data["capabilities"] = data["capabilities"].__dict__
        data["capabilities"]["control"] = data["capabilities"]["control"].__dict__
        data["capabilities"]["control"]["ct"] = data["capabilities"]["control"][
            "ct"
        ].__dict__
        data["capabilities"]["streaming"] = data["capabilities"]["streaming"].__dict__
        data["config"] = data["config"].__dict__
        data["config"]["startup"] = data["config"]["startup"].__dict__
        return json.dumps(data)

    def populate_object(self, response_json) -> list:
        lights = []
        for light_id, light_info in response_json.items():
            state = light_info["state"]
            swupdate = light_info["swupdate"]
            capabilites = light_info["capabilities"]
            control = capabilites["control"]
            ct = control["ct"]
            streaming = capabilites["streaming"]
            config = light_info["config"]
            startup = config["startup"]

            lights.append(
                PhilipsLightModel(
                    light_id,
                    State(
                        state["on"],
                        state["bri"],
                        state["hue"],
                        state["sat"],
                        state["effect"],
                        state["xy"],
                        state["ct"],
                        state["alert"],
                        state["colormode"],
                        state["mode"],
                        state["reachable"],
                    ),
                    Swupdate(swupdate["state"], swupdate["lastinstall"]),
                    light_info["type"],
                    light_info["name"],
                    light_info["modelid"],
                    light_info["manufacturername"],
                    light_info["productname"],
                    Capabilities(
                        capabilites["certified"],
                        Control(
                            control["mindimlevel"],
                            control["maxlumen"],
                            control["colorgamuttype"],
                            control["colorgamut"],
                            CT(ct["min"], ct["max"]),
                        ),
                        Streaming(streaming["renderer"], streaming["proxy"]),
                    ),
                    Config(
                        config["archetype"],
                        config["function"],
                        config["direction"],
                        Startup(startup["mode"], startup["configured"]),
                    ),
                    light_info["uniqueid"],
                    light_info["swversion"],
                    light_info["swconfigid"],
                    light_info["productid"],
                )
            )
        return lights

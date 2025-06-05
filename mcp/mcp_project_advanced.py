import re
import json
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from abc import ABC, abstractmethod
import logging
from typing import Dict, Optional

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- Enums & Data Classes ---

class LightState(Enum):
    ON = auto()
    OFF = auto()

class SecurityState(Enum):
    ARMED = auto()
    DISARMED = auto()

@dataclass
class DeviceStatus:
    lights: LightState = LightState.OFF
    temperature: int = 22
    security: SecurityState = SecurityState.DISARMED

@dataclass
class RoomContext:
    name: str
    devices: DeviceStatus = field(default_factory=DeviceStatus)

@dataclass
class HomeContext:
    rooms: Dict[str, RoomContext] = field(default_factory=dict)
    default_room: str = "living room"

    def __post_init__(self):
        # Ensure default room exists
        if self.default_room not in self.rooms:
            self.rooms[self.default_room] = RoomContext(name=self.default_room)

    def get_room(self, room_name: Optional[str] = None) -> RoomContext:
        room_name = room_name or self.default_room
        if room_name not in self.rooms:
            self.rooms[room_name] = RoomContext(name=room_name)
            logger.info(f"Added new room to context: {room_name}")
        return self.rooms[room_name]

    def save_to_file(self, filepath="home_context.json"):
        try:
            def serialize(obj):
                if isinstance(obj, Enum):
                    return obj.name
                raise TypeError(f"Type {type(obj)} not serializable")

            with open(filepath, 'w') as f:
                json.dump(asdict(self), f, indent=4, default=serialize)
            logger.info(f"Home context saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save context: {e}")

    @staticmethod
    def load_from_file(filepath="home_context.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            rooms = {}
            for rname, rdata in data.get("rooms", {}).items():
                devices = DeviceStatus(
                    lights=LightState[rdata["devices"]["lights"]],
                    temperature=rdata["devices"]["temperature"],
                    security=SecurityState[rdata["devices"]["security"]]
                )
                rooms[rname] = RoomContext(name=rname, devices=devices)
            default_room = data.get("default_room", "living room")
            logger.info(f"Loaded home context from {filepath}")
            return HomeContext(rooms=rooms, default_room=default_room)
        except FileNotFoundError:
            logger.warning(f"No saved context found at {filepath}, creating new.")
            return HomeContext()
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            return HomeContext()

# --- Abstract Model Interface ---

class SmartHomeModel(ABC):
    @abstractmethod
    def process_query(self, query: str, context: HomeContext) -> (str, HomeContext):
        pass

# --- Implementation of a Rule-Based Model ---

class RuleBasedSmartHomeModel(SmartHomeModel):

    TEMPERATURE_RANGE = (15, 30)

    def process_query(self, query: str, context: HomeContext) -> (str, HomeContext):
        query = query.lower().strip()
        logger.debug(f"Processing query: {query}")

        # Extract room if mentioned e.g. "in bedroom"
        room_match = re.search(r'in (\w+)', query)
        room_name = room_match.group(1) if room_match else None
        room = context.get_room(room_name)

        # Command parsing helpers
        def set_temperature(temp_val: int):
            if self.TEMPERATURE_RANGE[0] <= temp_val <= self.TEMPERATURE_RANGE[1]:
                room.devices.temperature = temp_val
                return f"Temperature in the {room.name} set to {temp_val}°C."
            else:
                return f"Temperature must be between {self.TEMPERATURE_RANGE[0]}°C and {self.TEMPERATURE_RANGE[1]}°C."

        def lights_on_off(turn_on: bool):
            if turn_on:
                if room.devices.lights == LightState.ON:
                    return f"The lights in the {room.name} are already ON."
                room.devices.lights = LightState.ON
                return f"Turning on lights in the {room.name}."
            else:
                if room.devices.lights == LightState.OFF:
                    return f"The lights in the {room.name} are already OFF."
                room.devices.lights = LightState.OFF
                return f"Turning off lights in the {room.name}."

        def security_arm_disarm(arm: bool):
            if arm:
                if room.devices.security == SecurityState.ARMED:
                    return f"The security system in the {room.name} is already ARMED."
                room.devices.security = SecurityState.ARMED
                return f"Security system in the {room.name} is now ARMED."
            else:
                if room.devices.security == SecurityState.DISARMED:
                    return f"The security system in the {room.name} is already DISARMED."
                room.devices.security = SecurityState.DISARMED
                return f"Security system in the {room.name} is now DISARMED."

        # Query routing & handling
        if re.search(r'turn on (the )?lights', query):
            return lights_on_off(True), context

        if re.search(r'turn off (the )?lights', query):
            return lights_on_off(False), context

        if re.search(r'(what(\'s| is) the )?temperature', query):
            temp = room.devices.temperature
            return f"The current temperature in the {room.name} is {temp}°C.", context

        temp_set_match = re.search(r'set (the )?temperature to (\d+)', query)
        if temp_set_match:
            temp_val = int(temp_set_match.group(2))
            return set_temperature(temp_val), context

        if re.search(r'arm (the )?security', query):
            return security_arm_disarm(True), context

        if re.search(r'disarm (the )?security', query):
            return security_arm_disarm(False), context

        if query in ["help", "commands"]:
            return (
                "You can control your smart home with commands like:\n"
                "- Turn on/off the lights [in <room>]\n"
                "- Set temperature to <value> [in <room>]\n"
                "- What's the temperature [in <room>]\n"
                "- Arm/disarm the security [in <room>]\n"
                "- Show status [of <room>]\n"
                "- Exit or quit\n",
                context
            )

        if re.search(r'show (me )?(the )?status', query):
            status_msgs = []
            for rname, rcontext in context.rooms.items():
                status_msgs.append(
                    f"{rname.title()}: Lights={rcontext.devices.lights.name}, "
                    f"Temp={rcontext.devices.temperature}°C, "
                    f"Security={rcontext.devices.security.name}"
                )
            return "\n".join(status_msgs), context

        if query in ["exit", "quit"]:
            return "Goodbye! Have a great day!", context

        # Default fallback
        return "Sorry, I didn't understand that command. Type 'help' for options.", context


# --- Main Program ---

def run_smart_home_assistant():
    print("Welcome to the Advanced Smart Home Assistant!")
    print("Type 'help' for available commands.")
    context = HomeContext.load_from_file()
    model = RuleBasedSmartHomeModel()

    while True:
        try:
            query = input("\nYou: ").strip()
            if not query:
                continue

            response, context = model.process_query(query, context)
            print(f"Assistant: {response}")

            # Save state after each command
            context.save_to_file()

            if query.lower() in ['exit', 'quit']:
                logger.info("Assistant session ended by user command.")
                break

        except KeyboardInterrupt:
            print("\nAssistant: Goodbye! (Interrupted)")
            logger.info("Assistant session interrupted by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print("Assistant: Sorry, something went wrong. Please try again.")

if __name__ == "__main__":
    run_smart_home_assistant()

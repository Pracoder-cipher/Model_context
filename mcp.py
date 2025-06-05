# mcp_project_improved.py

from dataclasses import dataclass, field
from enum import Enum, auto
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 1. Structured Context with Dataclasses
class LightState(Enum):
    ON = auto()
    OFF = auto()

@dataclass
class HomeContext:
    lights: LightState = LightState.OFF
    temperature: int = 22
    user_location: str = "living room"
    # Add more context variables as needed, with default values

    def __post_init__(self):
        """Post-initialization for validation."""
        if not (10 <= self.temperature <= 35): # More realistic temp range
            logger.warning(f"Initial temperature {self.temperature}°C is outside typical comfortable range.")
            # mcp_project_improved.py (continued)

from abc import ABC, abstractmethod

# 2. Abstract Base Class for "Model" Interface
class SmartHomeModel(ABC):
    @abstractmethod
    def process_query(self, query: str, context: HomeContext) -> tuple[str, HomeContext]:
        """
        Processes a user query given the current home context.
        Returns the model's response and the updated context.
        """
        pass
# mcp_project_improved.py (continued)

class RuleBasedSmartHomeModel(SmartHomeModel):
    def process_query(self, query: str, context: HomeContext) -> tuple[str, HomeContext]:
        response = ""
        updated_context = context # Start with current context, modify a copy if desired, or pass back the same mutable object.

        # Lowercase the query for case-insensitive matching
        query_lower = query.lower()

        # Handle lights
        if "turn on lights" in query_lower or "switch on lights" in query_lower:
            if updated_context.lights == LightState.OFF:
                response = "Turning on the lights."
                updated_context.lights = LightState.ON
                logger.info("Lights turned ON.")
            else:
                response = "The lights are already on."
                logger.info("Lights already ON, no action taken.")
        elif "turn off lights" in query_lower or "switch off lights" in query_lower:
            if updated_context.lights == LightState.ON:
                response = "Turning off the lights."
                updated_context.lights = LightState.OFF
                logger.info("Lights turned OFF.")
            else:
                response = "The lights are already off."
                logger.info("Lights already OFF, no action taken.")

        # Handle temperature
        elif "what's the temperature" in query_lower:
            response = f"The current temperature is {updated_context.temperature}°C."
        elif "set temperature to" in query_lower:
            try:
                # Extract temperature from query
                temp_value_str = ''.join(filter(str.isdigit, query_lower))
                if temp_value_str:
                    temp_value = int(temp_value_str)
                    if 18 <= temp_value <= 28: # Arbitrary sensible range
                        response = f"Setting temperature to {temp_value}°C."
                        updated_context.temperature = temp_value
                        logger.info(f"Temperature set to {temp_value}°C.")
                    else:
                        response = "That temperature is outside the comfortable range (18-28°C)."
                        logger.warning(f"Attempted to set temperature to {temp_value}°C, which is out of range.")
                else:
                    response = "Please specify a valid temperature (e.g., 'set temperature to 24')."
            except ValueError:
                response = "I couldn't understand the temperature. Please use a number."
                logger.error(f"Failed to parse temperature from query: '{query}'")

        if not response:
            response = "I'm not sure how to respond to that."
            logger.info(f"No specific response for query: '{query}'")

        return response, updated_context


# mcp_project_improved.py (continued)

def run_smart_home_assistant():
    # Initialize the specific model implementation
    model = RuleBasedSmartHomeModel()
    
    # Initialize the context using our structured dataclass
    home_context = HomeContext(lights=LightState.OFF, temperature=22) 
    logger.info(f"Initial Home Context: {home_context}")

    print("Welcome to the Improved Smart Home Assistant!")
    print("Type 'exit' to quit.")

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() == 'exit':
            print("Goodbye!")
            logger.info("Assistant session ended.")
            break

        # Pass the current home_context to the model and get an updated one
        response, updated_context = model.process_query(user_query, home_context)
        
        # Update the application's context with the one returned by the model
        home_context = updated_context

        print(f"Assistant: {response}")
        print(f"Current Home State: Lights={home_context.lights.name}, Temperature={home_context.temperature}°C")

if __name__ == "__main__":
    run_smart_home_assistant()

# mcp_project.py (continued)
# mcp_project.py

def smart_home_model(query: str, context: dict) -> str:
    """
    A simplified "smart home" AI model that responds based on query and context.
    Our Model Context Protocol is the 'context' dictionary.
    """
    response = ""

    # Check for context about lights
    if "lights" in context:
        light_state = context["lights"]
        if "turn on lights" in query.lower() or "switch on lights" in query.lower():
            if light_state == "off":
                response = "Turning on the lights."
                context["lights"] = "on" # Simulate state change
            else:
                response = "The lights are already on."
        elif "turn off lights" in query.lower() or "switch off lights" in query.lower():
            if light_state == "on":
                response = "Turning off the lights."
                context["lights"] = "off" # Simulate state change
            else:
                response = "The lights are already off."

    # Check for context about temperature
    if "temperature" in context:
        current_temp = context["temperature"]
        if "what's the temperature" in query.lower():
            response = f"The current temperature is {current_temp}°C."
        elif "set temperature to" in query.lower():
            try:
                # Extract temperature from query
                temp_value = int(''.join(filter(str.isdigit, query)))
                if 18 <= temp_value <= 28: # Arbitrary sensible range
                    response = f"Setting temperature to {temp_value}°C."
                    context["temperature"] = temp_value # Simulate state change
                else:
                    response = "That temperature is outside the comfortable range."
            except ValueError:
                response = "Please specify a valid temperature."

    if not response:
        response = "I'm not sure how to respond to that."

    return response
def main():
    # Our initial context for the model
    current_home_context = {
        "lights": "off",
        "temperature": 22,
        "user_location": "living room"
    }

    print("Welcome to the Smart Home Assistant!")
    print("Type 'exit' to quit.")

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break

        # Pass the current_home_context (our MCP) to the model
        model_response = smart_home_model(user_query, current_home_context)
        print(f"Assistant: {model_response}")
        print(f"Current Home Context (after interaction): {current_home_context}") # Show context update

if __name__ == "__main__":
    main()
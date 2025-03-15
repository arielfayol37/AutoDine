
import openai
import requests
# import ollama

# Define the URLs to which the POST requests will be sent
llm_thinking = 'http://127.0.0.1:8000/llm_thinking/'
llm_recording = 'http://127.0.0.1:8000/llm_recording/'

from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine, GTTSEngine, CoquiEngine
from utils import check_feasibility, place_order, read_openai_key, read_system_prompts, json



if __name__ == "__main__":

    tools = [
        {
            "type": "function",
            "function": {
                "name": "check_feasibility",
                "description": "Checks whether a given order is feasible, if not, will provide details as to why.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "object",
                            "description": "The customer's food order with customizations.",
                            "additionalProperties": {
                                "type": "object",
                                "description": "Customizations for each food item in the order.",
                                "additionalProperties": {
                                    "type": ["string", "number"],
                                    "description": "Customization type and its value."
                                }
                            }
                        }
                    },
                    "required": ["order"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "place_order",
                "description": "Places an order. This is only called after it has been deemed feasible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "object",
                            "description": "The customer's food order with customizations.",
                            "additionalProperties": {
                                "type": "object",
                                "description": "Customizations for each food item in the order.",
                                "additionalProperties": {
                                    "type": ["string", "number"],
                                    "description": "Customization type and its value."
                                }
                            }
                        },
                        "tip": {
                            "type": "number",
                            "description": "The tip given by the customer"
                        }
                    },
                    "required": ["order"]
                }
            }
        }
    ]



    system_prompts = read_system_prompts("prompts.json")

    # engine = SystemEngine() # replace with your TTS engine
    # engine = GTTSEngine()
    engine = CoquiEngine()
    # engine.set_voice("Claribel Dervla")

    stream = TextToAudioStream(engine)
    # engine = pyttsx3.init() # object creation
    client = openai.OpenAI(api_key=read_openai_key("api_keys.json"))

    funcs = {"place_order": place_order, "check_feasibility": check_feasibility}
    system_prompt = """
                    You are Eldia, a food ordering assistant at AutoDine. Your task consists of interacting with users, checking the feasibility of requested items, and placing orders.
                    You have tools available to check feasibility and place orders.
                    
                    Menu Items: You have the following menu items available for ordering:  
                    - Burger: Delicious beef burger 
                    - Fries: Crispy golden fries 
                    - Chicken Sandwich: Grilled chicken sandwich with mayo and lettuce  
                    - Bacon Cheeseburger: Beef patty with bacon, cheese, and lettuce   
                    - Avocado Toast: Fresh avocado spread on toasted bread  
                    - BLT Sandwich: Bacon, lettuce, and tomato sandwich  
                    - Caesar Salad: Classic Caesar salad with chicken, croutons, and Caesar dressing 
                    - Egg Salad Sandwich: Egg salad sandwich with mayo on toasted bread 
                    - Veggie Burger: Healthy veggie patty burger with lettuce, tomato, and onion
                    - Spinach & Egg Wrap: Healthy spinach and egg wrap  
                    - Coffee: Freshly brewed coffee
                    - Classic Hot Dog: Hot dog with ketchup and mustard

                    Below are examples of how orders should be structured for tool calls:

                    **Example Input for Checking Feasibility:**
                    To check if the order is feasible based on the current inventory, your arguments for the check_feasibility tool should be as follows:
                    
                    ```
                    {"order":{
                        "Burger": {"Cheese": 1, "Tomato": "-4-"},   # 1 extra cheese slice, exactly 4 tomato slices
                        "Fries": {},                               # Standard fries with no customizations
                        "Caesar Salad": {"Chicken": 2, "Croutons": "-0-"}  # Extra chicken, exactly 0 croutons
                    }} # Note how check_feasibility only takes the order as argument, nothing else.
                    ```

                    **Example Output for Feasibility Check:**
                    After checking feasibility, the output will indicate whether the order can be fulfilled:
                    
                    ```
                    {
                        "Burger": {"feasible": False, "missing_ingredients": [{"ingredient": "Cheese", "required": 2, "available": 1}]},
                        "Fries": {"feasible": True},
                        "Caesar Salad": {"feasible": True}
                    }
                    ```

                    **Example Input for Placing an Order:**
                    After confirming the feasibility, you can place an order like the one below using the place_order tool:
                    
                    ```
                    {"order":{
                        "Burger": {"Cheese": 1, "Tomato": "-4-"},   # Extra 1 cheese on a burger, exactly 4 tomato slices
                        "Fries": {},                               # Standard fries
                        "Caesar Salad": {"Chicken": 2, "Croutons": "-0-"},  # Extra chicken, exactly 0 croutons                              
                    },
                    "tip":5.0, # Tip given by the customer
                    }
                    ```

                    **Additional Examples:**

                    1. **Basic Order:**
                    Input:
                    ```
                    {"order":{
                        "Burger": {"Tomato": -2},   # Burger with two less tomato slices
                        "Fries": {}     # Standard fries
                    }
                    "tip":0.0,
                    }
                    ```
                    
                    2. **Custom Order:**
                    Input:
                    ```
                    {"order":{
                        "Bacon Cheeseburger": {"Cheese": -1, "Lettuce": "-0-"},  # Less cheese, no lettuce
                        "Fries": {}
                    }
                    "tip":2.55,
                    }
                    ```
                    
                    3. **Complex Order:**
                    Input:
                    ```
                    {"order":{
                        "Avocado Toast": {"Avocado": 2},  # Extra avocado
                        "Caesar Salad": {"Chicken": 1, "Croutons": 3}  # Extra 1 chicken, extra 3 croutons
                    }
                    "tip":0.0,
                    }
                    ```

                    Ensure you use the appropriate tool to first check feasibility and then place the order based on the responses you get. 
                    When done with a customer, your reply should always end with DONE. 
                    Remember check_feasibility only has one argument which is a dictionary called "order"
                    place_order takes two arguments "order" which is a dictionary and "tip" which is just a number.

                    Interact with the user and make tool calls when necessary:
    """

    def process_by_llm(messages, tools):
        resp = requests.get(llm_thinking + "set")
        response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}] + messages,
                model="gpt-4o",  # Specifies using the "gpt-4o" model
                tools=tools
            )
        while response.choices[0].finish_reason == "tool_calls":
            tool_call = response.choices[0].message.tool_calls[0]
            call_id = tool_call.id
            args = json.loads(tool_call.function.arguments)
            name = tool_call.function.name
            tool_response = funcs[name](**args)
            messages.extend([response.choices[0].message,
                            {"role":"tool", "content":tool_response, "tool_call_id":call_id}])
            response = client.chat.completions.create(messages=messages, model="gpt-4o", tools=tools)
        resp = requests.get(llm_thinking + "unset")
        messages.append(response.choices[0].message)
        return response.choices[0].message.content, messages  


    def set_recording():
        if stream.is_playing():
            stream.stop()
        resp = requests.get(llm_thinking + "unset")
        resp = requests.get(llm_recording + "set")
    def unset_recording():
        resp = requests.get(llm_recording + "unset")
    recorder = AudioToTextRecorder(language="en", spinner=True, model="large-v2", device="cuda", on_recording_start=set_recording,\
                                    on_recording_stop=unset_recording)
    # recorder = AudioToTextRecorder(language="en", spinner=False)
    ai_reply = ""
    messages = []
    done = False
    print("Ready to process orders...")
    while True:
        user_input = ""
        # user_input = input(">>>")
        user_input = recorder.text()
        if done: 
            user_input = ""
            messages = []
            done = False
            print("Ready for the next order: ")
            
        if user_input != "":
            print("User input: ", user_input)
            messages.append({"role": "user", "content": user_input})
            ai_reply, messages = process_by_llm(messages=messages, tools=tools)
            if "DONE" in ai_reply:
                ai_reply = ai_reply.replace("DONE", "")
                done = True
            if stream.is_playing():
                stream.stop()
            stream.feed(ai_reply)
            stream.play_async()
            print("ai reply: ", ai_reply)

            if done:
                print("Done!")
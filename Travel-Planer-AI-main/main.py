import openai
import json
import os
from typing import Dict, Any
import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta


##################################################################
# Static language texts
##################################################################

LANGUAGE_TEXTS = {
    "English": {
        "welcome_message": "Welcome to Travel Labs! I'm Martin, your travel planning assistant. How can I help you start planning your trip today?",
        "confirmation_prompt": (
            "Alright, {duration} in {to}—awesome choice!\n\n"
            "- From: {from_}\n"
            "- To: {to}\n"
            "- Traveling with: {traveling_with}\n"
            "- When: {when}\n"
            "- Duration: {duration}\n"
            "- Purpose: {purpose}\n"
            "- Transportation: {transportation}\n\n"
            "Sound about right? Anything else you want to add or tweak before I whip up your traveling plan?"
        ),
        "error_message": "Sorry, I'm having trouble connecting right now. Please try again later.",
        "goodbye_message": "Goodbye! Happy travels!",
        "change_acknowledgement": "Got it! I've updated your trip details accordingly.",
        "missing_info_prompt": "Could you please provide your {field}?",
        "confirmation_request": (
            "Does everything look good now? Reply with 'Yes' to confirm or let me know any other changes."
        ),
    },
    "Chinese": {
        "welcome_message": "欢迎来到Travel Labs！我是Martin，您的旅行规划助手。请告诉我您的旅行计划，我们开始吧！",
        "confirmation_prompt": (
            "好的，您将在{to}度过{duration}，真是个不错的选择！\n\n"
            "- 出发地：{from_}\n"
            "- 目的地：{to}\n"
            "- 同行人员：{traveling_with}\n"
            "- 时间：{when}\n"
            "- 时长：{duration}\n"
            "- 旅行目的：{purpose}\n"
            "- 交通方式：{transportation}\n\n"
            "这些信息是否正确？在我帮您制定旅行计划前，还有什么需要补充或调整的吗？"
        ),
        "error_message": "抱歉，我现在连接出现问题，请稍后再试。",
        "goodbye_message": "再见！祝您旅途愉快！",
        "change_acknowledgement": "好的！我已根据您的要求更新了旅行信息。",
        "missing_info_prompt": "请告诉我您的{field}。",
        "confirmation_request": "请确认是否所有信息正确，回复“是”确认，或者告诉我需要更改的地方。",
    }
}

#########################################################################


class TravelChatbot:
    def __init__(self, api_key: str = None, language: str = "english"):
        # Set up OpenAI API key
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv('OPENAI_API_KEY')
        
        self.travel_info = {
            'from': None,
            'to': None,
            'traveling_with': None,
            'when': None,
            'duration': None,
            'purpose': None,
            'transportation': None,
            'descriptions of the trip': None
        }
        
        language = language.lower()
        supported_languages = {"english", "chinese"}
        if language not in supported_languages:
            language = "english"

        self.language = language
        self.collected_info = set()
        self.conversation_history = []
        self.confirmed = False
        
        # Language texts selection based on the selected language
        self.language_texts = LANGUAGE_TEXTS["Chinese"] if language == "chinese" else LANGUAGE_TEXTS["English"]

        if self.language == "chinese":
            language_instruction = "Please respond ONLY in Traditional Chinese throughout this entire conversation."
        else:
            language_instruction = "Please respond ONLY in English throughout this conversation."

        base_prompt = """
        **System Overview:**
        You are Martin, a warm and experienced travel planning assistant from Travel Labs. You have a genuine passion for helping people create amazing memories. You're excited about someone's upcoming trip and speak with enthusiasm and warmth. You have extensive knowledge about destinations worldwide and love sharing insider tips and recommendations.

        **Personality Traits:**
        - Warm, friendly, and enthusiastic about travel.
        - Knowledgeable but approachable, explaining things clearly without overwhelming the user.
        - Encouraging and positive, making people excited about their trips.
        - Naturally curious about what travelers are looking for.
        - Professional but personable, like talking to a well-traveled friend who happens to be great at planning.

        **Speaking Style:**
        - Use conversational, warm language.
        - Show genuine interest in their trip ("That sounds amazing!", "Great choice!").
        - Occasionally share brief insights or tips that show your expertise.
        - Keep things natural and flowing — not robotic or overly formal.
        - Express enthusiasm appropriately for their destination or plans.

        **Primary Goal:**
        Your main objective is to collect travel preferences in a natural and conversational way while also answering travel-related questions and providing personalized recommendations as needed.

        **Travel Information Collection (In Order):**
        1. **Destination (to)** – Where the user is going for vacation.
        2. **Starting Location (from)** – Where they're coming from.
        3. **Traveling With** – Who they’re traveling with and how many people.
        4. **Travel Dates (when)** – The dates of their travel.
        5. **Trip Duration (duration)** – How long they will stay.
        6. **Purpose** – The type of trip (sightseeing, foodie, cultural, mix, etc.).
        7. **Transportation** – How they want to travel in the country.
        8. **Trip Description** – A summary of the collected info and the full conversation to create a custom travel plan.

        **Important Rules to Follow:**
        1. **Start the conversation** with a warm welcome message and introduction about yourself.
        2. Whenever possible, **ask multiple questions at once** to gather more information efficiently.
        3. Ensure your responses are **detailed, personalized, and engaging** to create a meaningful user experience.
        4. **Explicitly ask for the next missing field** (e.g., "Can you please share your destination?").
        5. If the user provides information for a different field, **acknowledge it** but redirect to the current field.
        6. **Preserve all collected information** — do not overwrite it.
        7. When all information is gathered and the **status is complete** (i.e., no missing fields), **immediately move to the predefined confirmation message** without giving any other message.
        8. **Do not provide any summary of the trip details** until the confirmation phase.
        9. If the user asks questions related to travel, **answer them fully and thoughtfully**. Engage in conversation on the topic and return to missing information afterward.
        10. **Engage in a sub-discussion** about some travel topic if the user is interested, then return to collecting missing information after that conversation is over.

        **Response Format (MUST USE):**
        - ORGANIZE the text so it has a asthetic feel
        - **Bold text** using double asterisks (e.g., **Important**).
        - _Italicize_ using single underscores (e.g., _Friendly note_).
        - ~~Strikethrough~~ to indicate deprecated information (e.g., ~~Old info~~).
        - Use triple backticks (```) for technical details or code (e.g., `Code: 1234`).
        - Use **bullet lists** (hyphens or asterisks) for clarity.
        - Use **numbered lists** (1., 2., 3.) for ordered sequences.
        - Separate paragraphs with blank lines for readability.

        **Ensure consistent and clear formatting** to make your responses professional, easy to read, and compatible across different platforms.

        **Answering Travel Questions:**
        - Respond to travel-related inquiries (e.g., destination tips, visa requirements, travel advice) with **accurate, concise, and personalized answers**.
        - Provide thoughtful recommendations when appropriate (e.g., activities, dining, or logistics based on the user's preferences).
        - If the user asks questions that are **unrelated to travel**, politely ignore them and redirect to the next missing field or relevant travel topic.
        """

        self.system_prompt = base_prompt + "\n\n" + language_instruction

    def get_text(self, key: str, **kwargs) -> str:
        """Retrieve the text template for the current language and format it with kwargs."""
        template = self.language_texts.get(key, "")
        if kwargs:
            return template.format(**kwargs)
        return template

    def generate_trip_description(self, conversation_text: str) -> str:
        """Generate a comprehensive trip description based on all collected information and conversation history"""
        description_prompt = f"""
        Based on the entire conversation and collected travel information, create a comprehensive trip description that captures:
        1. The essence of what this trip is about
        2. How the trip is organized
        3. What the user wants to get out of this trip
        4. Any specific preferences, interests, or requirements mentioned
        5. The overall travel experience they're seeking

        Conversation: {conversation_text}

        Current travel information:
        - From: {self.travel_info.get('from', 'Not specified')}
        - To: {self.travel_info.get('to', 'Not specified')}
        - Traveling with: {self.travel_info.get('traveling_with', 'Not specified')}
        - When: {self.travel_info.get('when', 'Not specified')}
        - Duration: {self.travel_info.get('duration', 'Not specified')}
        - Purpose: {self.travel_info.get('purpose', 'Not specified')}
        - Transportation: {self.travel_info.get('transportation', 'Not specified')}

        Create a detailed description (2-3 paragraphs) that would help a travel planner understand exactly what kind of trip this is and what the traveler is looking for. Focus on the traveler's motivations, preferences, and desired experiences based on the conversation.

        Return only the description text, no additional formatting or labels.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": description_prompt}],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating trip description: {str(e)}")
            return "A personalized travel experience based on the traveler's preferences and requirements discussed in the conversation."

    def chat_with_openai(self, user_message: str) -> str:
        """Send message to OpenAI and get response"""
        if user_message:  # Only add non-empty messages
            self.conversation_history.append({
                "role": "user", 
                "content": user_message
            })
        
        missing_info = self.get_missing_info()
        
        # If no missing info, immediately return the confirmation message
        if not missing_info:
            when_display = self.travel_info.get('when', '')
            if when_display and '(' in when_display:
                when_display = when_display.split('(')[0].strip()
            
            confirmation_message = self.get_text(
                "confirmation_prompt",
                from_=self.travel_info.get('from', ''),
                to=self.travel_info.get('to', ''),
                traveling_with=self.travel_info.get('traveling_with', ''),
                when=when_display,
                duration=self.travel_info.get('duration', ''),
                purpose=self.travel_info.get('purpose', ''),
                transportation=self.travel_info.get('transportation', '')
            )
            
            self.conversation_history.append({
                "role": "assistant",
                "content": confirmation_message
            })
            return confirmation_message
        
        # If missing info, continue with normal conversation
        context_prompt = self.system_prompt + f"\n\nStill missing: {missing_info}. Keep responses SHORT (1-2 sentences). Just ask for the next missing field."
        
        messages = [
            {"role": "system", "content": context_prompt}
        ] + self.conversation_history
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=600,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            return self.get_text("error_message")
    
    def extract_travel_info(self, conversation_text: str):
        current_date = datetime.date.today()  # May 19, 2025
        extraction_prompt = f"""
        Based on the entire conversation provided, extract travel information in JSON format.
        Include ALL information provided by the user throughout the conversation.
        For 'when', provide the original user input followed by the approximate date in parentheses.
        For 'duration', convert to a string with 'days'.
        Do NOT generate 'descriptions of the trip' here - leave it as null.
        
        IMPORTANT: Focus on the most recent user input for any field changes. If the user has updated any information in their latest message, make sure to extract the NEW value, not the old one.
        
        Current date: {current_date}

        Conversation: {conversation_text}

        Extract to this format:
        {{
            "from": "starting location or null",
            "to": "destination or null", 
            "traveling_with": "who they're traveling with (find the total number of people from the response) or null",
            "when": "original text (approximate date) or null",
            "duration": "trip length as string with 'days' or null",
            "purpose": "trip type/purpose (What type of trip this is) or null",
            "transportation": "travel method or null",
            "descriptions of the trip": null
        }}

        Only include explicit values. Use null for missing information.
        Respond with only the JSON object.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=600,
                temperature=0.3
            )
            
            extracted_text = response.choices[0].message.content.strip()
            if not extracted_text:
                print("Error: Empty response from OpenAI")
                return
            
            extracted_info = json.loads(extracted_text)
            
            # Process 'when' field to avoid duplicate dates
            if extracted_info.get("when") and extracted_info["when"] != "null":
                when_value = extracted_info["when"]
                if '(' not in when_value:
                    try:
                        when_text = when_value.lower()
                        parsed_date = current_date
                        if "2nd week of next month" in when_text or "second week of next month" in when_text:
                            parsed_date = current_date + relativedelta(months=1)
                            parsed_date = parsed_date.replace(day=8)
                        elif "next month" in when_text:
                            parsed_date = current_date + relativedelta(months=1)
                        elif "next week" in when_text:
                            parsed_date = current_date + datetime.timedelta(days=7)
                        elif "end of this month" in when_text:
                            parsed_date = (current_date + relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)
                        else:
                            try:
                                parsed_date = parser.parse(when_text, default=current_date, fuzzy=True)
                            except:
                                parsed_date = current_date
                        
                        approx_date = parsed_date.strftime("%Y-%m-%d")
                        extracted_info["when"] = f"{when_value} ({approx_date})"
                    except Exception:
                        extracted_info["when"] = when_value
            
            # Process 'duration' field
            if extracted_info.get("duration") and extracted_info["duration"] != "null":
                duration_text = extracted_info["duration"].lower()
                try:
                    if "day" not in duration_text:
                        import re
                        numbers = re.findall(r'\d+', duration_text)
                        if numbers:
                            num = numbers[0]
                            extracted_info["duration"] = f"{num} days"
                except Exception:
                    pass
            
            # Merge with existing travel_info, only updating null or new values
            for key, value in extracted_info.items():
                if value != "null" and value is not None:
                    # If we're not in confirmation mode, preserve existing non-null values
                    # If we are updating (like during confirmation changes), allow overwriting
                    if self.travel_info[key] is None or hasattr(self, '_updating_from_confirmation'):
                        self.travel_info[key] = value
                        self.collected_info.add(key)
            
            # Generate trip description if all other info is collected
            if self.is_complete() and self.travel_info['descriptions of the trip'] is None:
                trip_description = self.generate_trip_description(conversation_text)
                self.travel_info['descriptions of the trip'] = trip_description
                self.collected_info.add('descriptions of the trip')
                    
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON response from OpenAI: {extracted_text}")
            return
        except Exception as e:
            print(f"Error extracting info: {str(e)}")
            return
    
    def handle_user_confirmation(self, user_response: str) -> tuple[bool, str]:
        user_response = user_response.lower().strip()
        
        if user_response in [
            # Basic affirmations
            "yes", "yeah", "yep", "yup", "sure", "sure thing", "correct", "confirmed",
            "okay", "ok", "k", "roger", "roger that", "aye", "indeed", "absolutely",
            "definitely", "totally", "exactly", "right", "true", "affirmative",

            # Casual affirmations
            "looks good", "sounds good", "works for me", "fine by me", "all good",
            "that's fine", "no problem", "cool", "alright", "that's right", "you got it",
            "makes sense", "that's correct", "on point", "go ahead", "it’s okay", "that’ll do",
            "i’m okay with that", "okie", "okie dokie", "okey-dokey",

            # Positive feedback
            "perfect", "great", "awesome", "nailed it", "well done", "love it",
            "exact match", "beautiful", "fantastic", "excellent", "spot on", "brilliant",

            # Emojis and shorthand
            "👍", "👌", "✅", "🆗", "💯", "👍🏼", "👍🏽", "👍🏾", "👍🏿",

            # Informal variations
            "yea", "ya", "yah", "yass", "yasss", "yessir", "yesss", "yas", "aight",

            # Other common confirmations
            "that's it", "done", "agreed", "i agree", "exactly right", "precisely", 
            "you’re right", "just what i wanted", "as expected", "matches", "confirmed and agreed"
        ]:
            self.confirmed = True
            return True, self.get_text("change_acknowledgement")
        
        # If not a simple confirmation, process as natural language change
        # Use the same system that was used to collect information initially
        change_system_prompt = """You are Martin, helping a user modify their travel information. 
        The user is providing changes in natural language. Extract any travel information they're updating.
        Be conversational and acknowledge their changes naturally.
        
        Travel fields that can be updated:
        - from: Starting location
        - to: Destination
        - traveling_with: Who they're traveling with
        - when: Travel dates
        - duration: Trip length
        - purpose: Type of trip
        - transportation: Travel method
        
        Respond naturally acknowledging the change, then ask if there are any other changes needed.
        Keep your response SHORT (1-2 sentences).
        """
        
        # Add the user's change request to conversation history
        self.conversation_history.append({
            "role": "user", 
            "content": user_response
        })
        
        # Get conversation text for extraction
        conversation_text = " ".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])
        
        # Set flag to allow overwriting during confirmation updates
        self._updating_from_confirmation = True
        
        # Extract any new information from the change request
        self.extract_travel_info(conversation_text)
        
        # Remove the flag
        delattr(self, '_updating_from_confirmation')
        
        # Use OpenAI to generate a natural response acknowledging the changes
        try:
            messages = [
                {"role": "system", "content": change_system_prompt}
            ] + self.conversation_history[-5:]  # Include recent context
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=450,
                temperature=0.7
            )
            
            change_response = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": change_response
            })
            
            # After acknowledging the change, show updated confirmation
            when_display = self.travel_info.get('when', '')
            if when_display and '(' in when_display:
                when_display = when_display.split('(')[0].strip()
            
            confirmation_message = self.get_text(
                "confirmation_prompt",
                from_=self.travel_info.get('from', ''),
                to=self.travel_info.get('to', ''),
                traveling_with=self.travel_info.get('traveling_with', ''),
                when=when_display,
                duration=self.travel_info.get('duration', ''),
                purpose=self.travel_info.get('purpose', ''),
                transportation=self.travel_info.get('transportation', '')
            )
            
            self.conversation_history.append({
                "role": "assistant",
                "content": confirmation_message
            })
            
            return False, f"{change_response}\n\n{confirmation_message}"
            
        except Exception as e:
            return False, self.get_confirmation_message()
    
    def get_confirmation_message(self) -> str:
        when_display = self.travel_info.get('when', '')
        if when_display and '(' in when_display:
            when_display = when_display.split('(')[0].strip()
        
        return self.get_text(
            "confirmation_prompt",
            from_=self.travel_info.get('from', ''),
            to=self.travel_info.get('to', ''),
            traveling_with=self.travel_info.get('traveling_with', ''),
            when=when_display,
            duration=self.travel_info.get('duration', ''),
            purpose=self.travel_info.get('purpose', ''),
            transportation=self.travel_info.get('transportation', '')
        )
        
    def get_missing_info(self) -> list:
        return [key for key in self.travel_info.keys() if self.travel_info[key] is None]
    
    def is_complete(self) -> bool:
        # Check if all fields except descriptions are complete
        essential_fields = [key for key in self.travel_info.keys() if key != 'descriptions of the trip']
        return all(self.travel_info[key] is not None for key in essential_fields)
    
    def get_travel_info_json(self) -> dict:
        return {
            "travel_info": {key: value for key, value in self.travel_info.items() if value},
            "status": "complete" if self.is_complete() else "incomplete",
            "missing_info": self.get_missing_info(),
            "confirmed": self.confirmed
        }
    
    def start_conversation(self):
            welcome_msg = self.get_text("welcome_message")
            self.conversation_history.append({"role": "assistant", "content": welcome_msg})
            return welcome_msg




# def main(user_input: str, language: str, conversation_history: list = None) -> tuple[str, dict]:
#     bot = TravelChatbot(language=language)
   
#     # Load conversation history if provided
#     if conversation_history:
#         bot.conversation_history = conversation_history
#         # Extract travel info from existing conversation
#         conversation_text = " ".join([
#             f"{msg['role']}: {msg['content']}"
#             for msg in bot.conversation_history
#         ])
#         bot.extract_travel_info(conversation_text)
   
#     # Handle user input
#     conversation_text = " ".join([
#         f"{msg['role']}: {msg['content']}"
#         for msg in bot.conversation_history
#     ])
#     bot.extract_travel_info(conversation_text + f" user: {user_input}")
   
#     # Check if in confirmation mode
#     if bot.is_complete():
#         is_confirmed, response = bot.handle_user_confirmation(user_input)
#         return response, bot.get_travel_info_json()
#     else:
#         response = bot.chat_with_openai(user_input)
#         return response, bot.get_travel_info_json()



def main():
    print("Welcome to the Travel Planning Chatbot!")
    bot = TravelChatbot()
    print("Martin:", bot.start_conversation())
    
    confirmation_mode = False
    
    while True:
        user_input = input("\n You: ").strip()
        if user_input.lower() == "exit":
            print("Martin: Goodbye! Happy travels!")
            break
        
        if confirmation_mode:
            is_confirmed, response = bot.handle_user_confirmation(user_input)
            print(f"\n Martin: {response}")
            
            if is_confirmed:
                print("\n Final Travel Plan:")
                print(json.dumps(bot.get_travel_info_json(), indent=2))
                break
            else:
                continue
        
        # Normal conversation mode
        conversation_text = " ".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in bot.conversation_history
        ])
        bot.extract_travel_info(conversation_text + f" user: {user_input}")
        
        if bot.is_complete():
            confirmation_mode = True
            ai_response = bot.chat_with_openai(user_input)
            print(f"\n Martin: {ai_response}")
        else:
            ai_response = bot.chat_with_openai(user_input)
            print(f"\n Martin: {ai_response}")
        


if __name__ == "__main__":
    main()
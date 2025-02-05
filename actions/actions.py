import mysql.connector
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from typing import List, Dict, Any, Text



class ActionSetUserId(Action):
    def name(self) -> str:
        return "action_set_user_id"

    def run(self, dispatcher, tracker, domain):
        # Here you can set the user_id programmatically if you have it
        user_id = "2"  # You can retrieve this from a database or external service
        
        # Set the slot with the user_id
        return [SlotSet("user_id", user_id)]


class ActionFetchUserBalance(Action):
    def name(self) -> Text:
        return "action_fetch_user_balance"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the user ID from the slot
        user_id = tracker.get_slot("user_id")

        if not user_id:
            dispatcher.utter_message(text="Please provide your user ID.")
            return []

        try:
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="bankingbot",
                password="bankingbot",
                database="bankingbot"
            )
            cursor = conn.cursor()

            # Query to fetch the user's balance
            cursor.execute("SELECT balance, pin, name FROM users WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            

            # If no user data is found
            if not user_data:
                dispatcher.utter_message(text="Sorry {user_name}, we couldn't find your account.")
                return []

            # Extract the balance
            user_balance = user_data[0]
            user_pin = user_data[1]
            user_name = user_data[2]
            dispatcher.utter_message(text=f"{user_name}, Your current balance is ${user_balance}.")
            
            # Store the balance in the slot for further use
            return [SlotSet("user_balance", user_balance),
                    SlotSet("user_pin", str(user_pin))
                    ]

        except mysql.connector.Error as err:
            dispatcher.utter_message(text=f"An error occurred while accessing the database: {err}")
            return []

        finally:
            conn.close()


class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        transfer_amount = tracker.get_slot("amount")
        user_balance = tracker.get_slot("user_balance")

        if not transfer_amount:
            dispatcher.utter_message(text="Please enter a valid amount to transfer.")
            return []

        if transfer_amount > user_balance:
            #dispatcher.utter_message(text="You don't have enough funds to complete this transfer.")
            return [SlotSet("has_sufficient_funds", False)]
        else:
            #dispatcher.utter_message(text="You have sufficient funds to proceed with the transfer.")
            return [SlotSet("has_sufficient_funds", True)]
    

class ActionVerifyPin(Action):
    def name(self) -> Text:
        return "action_verify_pin"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entered_pin = tracker.get_slot("pin")
        correct_pin = str(tracker.get_slot("user_pin"))

        #print(f"Entered PIN: {entered_pin}")
        #print(f"Correct PIN: {correct_pin}")

        if entered_pin == correct_pin:
            dispatcher.utter_message(text="PIN verified successfully!")
            return [SlotSet("pin_verified", True)]
        else:
            #dispatcher.utter_message(text="The PIN you entered is incorrect. Please try again.")
            return [SlotSet("pin_verified", False), SlotSet("pin", None)]  # Clear the PIN slot




class ActionTransferMoney(Action):
    def name(self) -> Text:
        return "action_transfer_money"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the transfer amount and user balance
        transfer_amount = tracker.get_slot("amount")
        user_balance = tracker.get_slot("user_balance")
        user_id = tracker.get_slot("user_id")

        # Check if there is a sufficient balance
        if transfer_amount > user_balance:
            dispatcher.utter_message(text="You don't have enough funds to complete this transfer.")
            return []

        # Deduct the transfer amount from the balance
        new_balance = user_balance - transfer_amount

        try:
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="bankingbot",
                password="bankingbot",
                database="bankingbot"
            )
            cursor = conn.cursor()

            # Update the user's balance after the transfer
            cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
            conn.commit()

            # Notify the user about the successful transfer
            dispatcher.utter_message(text=f"Transfer of ${transfer_amount} was successful. Your new balance is ${new_balance}.")

            # Update the balance in the slot for future use
            return [SlotSet("user_balance", new_balance),
                    SlotSet("amount", None),
                    SlotSet("recipient", None),
                    SlotSet("pin", None),
                    SlotSet("final_confirmation", None),
                    SlotSet("user_pin", None),
                    SlotSet("pin_verified", None),
                    SlotSet("has_sufficient_funds", None)
                    ]

        except mysql.connector.Error as err:
            dispatcher.utter_message(text=f"An error occurred while processing the transfer: {err}")
            return []

        finally:
            conn.close()


class ActionSorryCouldntAnswer(Action):
    def name(self) -> str:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        dispatcher.utter_message(text="Sorry, I couldn't answer that question.")
        return []

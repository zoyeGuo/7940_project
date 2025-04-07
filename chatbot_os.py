import os
import json
import logging
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


TELEGRAM_ACCESS_TOKEN = os.environ.get("TELEGRAM_ACCESS_TOKEN")
CHATGPT_SERVICE_URL = os.environ.get("CHATGPT_SERVICE_URL")  
DBSERVICE_URL = os.environ.get("DBSERVICE_URL")             

if not TELEGRAM_ACCESS_TOKEN or not CHATGPT_SERVICE_URL or not DBSERVICE_URL:
    logging.error("Missing required environment variables: TELEGRAM_ACCESS_TOKEN, CHATGPT_SERVICE_URL, and DBSERVICE_URL")
    exit(1)

def submit_to_chatgpt(prompt):
    """Call the ChatGPT service endpoint to submit the prompt and return the response text."""
    try:
        resp = requests.post(CHATGPT_SERVICE_URL, json={"prompt": prompt}, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        else:
            return f"ChatGPT service error: status code {resp.status_code}"
    except Exception as e:
        return f"Error calling ChatGPT service: {str(e)}"

def db_insert(data):
    """Call the database service's /insert endpoint to insert data into Azure Cosmos DB."""
    try:
        url = f"{DBSERVICE_URL}/insert"
        resp = requests.post(url, json=data, timeout=30)
        if resp.status_code in (200, 201):
            return resp.json()
        else:
            return {"error": f"DB insert error, status code {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def db_query(rank):
    """Call the database service's /query endpoint to query user data based on rank."""
    try:
        url = f"{DBSERVICE_URL}/query"
        params = {"rank": rank}
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        else:
            return []
    except Exception as e:
        logging.error("DB query error: " + str(e))
        return []

def intent_analysis(user_input):
    """
    Call the ChatGPT service to analyze whether the user input expresses the intent to play csgo.
    Reply with exactly "yes" or "no" (no extra text).
    """
    intent_prompt = f"""
You are an intent analysis assistant. Determine whether the following user input expresses the intent to play csgo.
Reply with exactly "yes" or "no" (without quotes, no additional text or punctuation).
User input: {user_input}
"""
    result = submit_to_chatgpt(intent_prompt).strip().lower()
    first_word = result.split()[0] if result else ""
    if first_word == "yes":
        return "yes"
    else:
        return "no"

def info_extraction_first(user_input):
    """First call to ChatGPT to extract game information from the user input, output in JSON format only."""
    prompt = f"""
You are an information extraction assistant. Please extract the following information from the user input and output ONLY JSON with no extra text:
{{
    "game_id": "<Game ID>",
    "rank": "<Rank>",
    "contact": "<Contact Information>"
}}
If the user input is insufficient, leave the corresponding field empty.
User input: {user_input}
Output ONLY JSON with no explanations or extra text.
"""
    return submit_to_chatgpt(prompt)

def info_extraction_update(partial_info, new_input):
    """Based on existing partial information, update missing fields using new input; output only in JSON format."""
    prompt = f"""
You are an information extraction assistant. The user has already provided the following partial information (in JSON):
{json.dumps(partial_info, ensure_ascii=False)}

User new input: {new_input}

Please update and complete the missing fields using the following JSON format, and output ONLY JSON with no extra explanation or text:
{{
    "game_id": "<Game ID>",
    "rank": "<Rank>",
    "contact": "<Contact Information>"
}}
If no new information is provided for a field, retain the original value.
Output ONLY JSON with no additional content.
"""
    return submit_to_chatgpt(prompt)

def message_handler(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()

    # If in the state of collecting game information
    if context.user_data.get("expecting_game_info", False):
        required_fields = ["game_id", "rank", "contact"]

        # First extraction if no partial_info exists
        if "partial_info" not in context.user_data:
            json_response = info_extraction_first(user_input)
            try:
                user_info = json.loads(json_response)
            except Exception as e:
                update.message.reply_text("Unable to parse your information. Please ensure the format is correct and try again.")
                return

            missing_fields = [k for k in required_fields if not user_info.get(k) or not str(user_info.get(k)).strip()]
            if missing_fields:
                context.user_data["partial_info"] = user_info
                update.message.reply_text("The following fields are missing from your input, please provide them: " + ", ".join(missing_fields))
                return
            else:
                complete_info = user_info
        else:
            # If partial information exists; update with new input
            partial_info = context.user_data["partial_info"]
            json_response = info_extraction_update(partial_info, user_input)
            try:
                updated_info = json.loads(json_response)
            except Exception as e:
                update.message.reply_text("Unable to parse your information. Please ensure the format is correct and try again.")
                return

            # Merge updated info into partial_info
            for k in required_fields:
                val = updated_info.get(k)
                if val and str(val).strip():
                    partial_info[k] = val

            missing_fields = [k for k in required_fields if not partial_info.get(k) or not str(partial_info.get(k)).strip()]
            if missing_fields:
                context.user_data["partial_info"] = partial_info
                update.message.reply_text("The following fields are still missing, please continue to provide: " + ", ".join(missing_fields))
                return
            else:
                complete_info = partial_info

        # Once complete, call the DB service to insert data
        game_id = complete_info["game_id"]
        db_result = db_insert(complete_info)
        if "error" in db_result:
            update.message.reply_text("Error inserting data into the database: " + db_result["error"])
        else:
            # Query DB for users with the same rank
            rank = complete_info.get("rank")
            if rank:
                similar_users = db_query(rank)
                if similar_users:
                    reply = "Found the following users with the same rank:\n"
                    for u in similar_users:
                        reply += f"Game ID: {u.get('game_id')}, Rank: {u.get('rank')}, Contact: {u.get('contact')}\n"
                else:
                    reply = "No users with the same rank were found."
                update.message.reply_text(reply)
            else:
                update.message.reply_text("Unable to retrieve your rank information.")
        # Clear the collection state
        context.user_data.pop("partial_info", None)
        context.user_data["expecting_game_info"] = False
        return

    # If not in information collection state, perform intent analysis
    intent = intent_analysis(user_input)
    if intent == "yes":
        update.message.reply_text("I can help you find other csgo players. Please provide your Game ID, Rank, and Contact Information.")
        context.user_data["expecting_game_info"] = True
        return

    # Default: directly pass user input to the ChatGPT service for reply
    response = submit_to_chatgpt(user_input)
    update.message.reply_text(response)

def main():
    updater = Updater(token=TELEGRAM_ACCESS_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), message_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
from telethon.sync import TelegramClient
from telethon.tl.types import User, Channel
from telethon.tl.functions.channels import CreateChannelRequest
# from dotenv import load_dotenv
import asyncio
import os
# load_dotenv()

# .env sample file
GROQ_API_KEY="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"
API_ID="26553278"
API_HASH="1ba4cb64bb38d956faf3f2a33b2a0bba"

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

def create_new_group_or_channel(client):
    choice = input("\nDo you want to create a new Group or Channel? (yes/no): ").strip().lower()
    if choice == 'yes':
        name = input("Enter the name of the Group/Channel: ")
        description = input("Enter the description of the Group/Channel: ")
        is_channel = input("Is this a Channel? (yes/no): ").strip().lower() == 'yes'
        try:
            result = client(CreateChannelRequest(
                title=name,
                about=description,
                megagroup=not is_channel
            ))
            if is_channel:
                print(f"Channel '{name}' created successfully!")
            else:
                print(f"Group '{name}' created successfully!")
        except Exception as e:
            print(f"Error while creating the group/channel: {e}")
    else:
        print("Skipping group/channel creation.")



# def get_groups_and_bots(phone_number):
#     try:
#         with TelegramClient(f'session_{phone_number}', api_id, api_hash) as client:
#             dialogs = client.get_dialogs()
#             groups = []
#             bots = []
#             for dialog in dialogs:
#                 if isinstance(dialog.entity, Channel):
#                     groups.append(dialog.name)
#                 elif isinstance(dialog.entity, User) and dialog.entity.bot:
#                     bots.append(dialog.name)
#             print("\nGroups/Channels:")
#             print("\n".join(groups) if groups else "No groups or channels found.")
#             print("\nBots:")
#             print("\n".join(bots) if bots else "No bots found.")

#             create_new_group_or_channel(client)
#     except Exception as e:
#         print(f"Error: {e}")

# phone_number = input("Enter the phone number you authorized (with country code, e.g., +1234567890): ")



async def get_telegram_authorized_code(phone_number):
    print(phone_number,f'session_+91{phone_number}')
    try:
        client = TelegramClient(f'session_+91{phone_number}', API_ID, API_HASH)
        await client.connect()  # Use await to handle async connection
        await client.send_code_request(phone_number)  # Await the request
        return True
    except Exception as e:
        print(str(e))
        return False
        

    # Disconnect after sending the request (optional)
    # await client.disconnect()
    # try:
    #     client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
    #     client.connect()
    #     client.send_code_request(phone_number)
    #     return True
    # except Exception as e:
    #     print(str(e))
    #     return False




def get_groups_and_bots(phone_number,otp):
    
    try:
        client = TelegramClient(f'session_+91{phone_number}', API_ID, API_HASH)
        client.connect()

        if not client.is_user_authorized():
            # client.send_code_request(phone_number)
            client.sign_in(phone_number, otp)

        print(f"Connected as {phone_number}.")
        dialogs = client.get_dialogs()
        groups = []
        bots = []

        for dialog in dialogs:
            if isinstance(dialog.entity, Channel):
                groups.append(dialog.name)
            elif isinstance(dialog.entity, User) and dialog.entity.bot:
                bots.append(dialog.name)
        

    except Exception as e:
        print(f"Error: {e}")


    return groups

    # finally:
    #     client.disconnect()


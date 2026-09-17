import asyncio
import re
import random
import time
from telethon import TelegramClient, events

target_bot = 8416087176
target_bot_entity = None

api_id = '39300763'     
api_hash = 'ff7e61213afea67d31fa33d7e667e659'    
session_name = 'bish.session'
client = TelegramClient(session_name, api_id, api_hash)

last_hunt_sent_time = 0
waiting_for_hunt_response = False
is_in_battle = False
current_wild_pokemon = ""
hunt_lock = asyncio.Lock()
repeat_ball = []

ultra_ball = [
    "Abomasnow", "Abra", "Absol", "Accelgor", "Aerodactyl", "Aggron", "Alakazam", "Altaria", "Amaura", "Ampharos",
    "Applin", "Arceus", "Arrokuda", "Audino", "Axew", "Bagon", "Barraskewda", "Beedrill", "Beldum", "Bergmite",
    "Bewear", "Binacle", "Blastoise", "Blaziken", "Boltlund", "Braixen", "Brionne", "Bulbasaur", "Buneary", "Calyrex",
    "Camerupt", "Carbink", "Charizard", "Charjabug", "Charmander", "Charmeleon", "Chesnaught", "Chespin", "Chewtle", "Chimchar",
    "Cinderace", "Clauncher", "Cobalion", "Corviknight", "Cosmoem", "Cosmog", "Cufant", "Cutiefly", "Cyndaquil", "Cyndaquill",
    "Dartrix", "Darumaka", "Delphox", "Deoxys", "Dialga", "Diancie", "Diggersby", "Diglett", "Doduo", "Donphan",
    "Dracozolt", "Dragonite", "Drakloak", "Dratini", "Drilbur", "Druddigon", "Duraludon", "Durant", "Dwebble", "Eevee",
    "Electrike", "Electrode", "Elekid", "Empoleon", "Enamorus", "Espeon", "Eternatus", "Fennekin", "Feraligatr", "Ferroseed",
    "Flabebe", "Flaffy", "Fletchling", "Floette", "Flygon", "Formantis", "Fraxure", "Frillish", "Froakie", "Frogadier",
    "Furfrou", "Gabite", "Gallade", "Garchomp", "Gardevoir", "Genesect", "Gible", "Glalie", "Glastrier", "Golisopod",
    "Goodra", "Goomy", "Greninja", "Grimer", "Grimmsnarl", "Grookey", "Grotle", "Groudon", "Gurdurr", "Gyarados",
    "Hakamo-o", "Hawlucha", "Haxorus", "Heatran", "Helioptile", "Heracross", "Ho-oh", "Honedge", "Houndoom", "Impidimp",
    "Infernape", "Inkay", "Inteleon", "Ivysaur", "Jangmo-o", "Jolteon", "Joltik", "Kangaskhan", "Karrablast", "Kirlia",
    "Klefki", "Kommo-o", "Krokorok", "Krookodile", "Kubfu", "Kyogre", "Kyurem", "Landorus", "Larvesta", "Larvitar",
    "Leafeon", "Litleo", "Litten", "Lopunny", "Lotad", "Lucario", "Lugia", "Lycanroc", "Machamp", "Machop",
    "Magearna", "Magikarp", "Magmar", "Magmortar", "Manectric", "Mankey", "Mareabnie", "Mareep", "Mawile", "Medicham",
    "Meowth", "Mewtwo", "Monferno", "Mudbray", "Mudkip", "Munchlax", "Nincada", "Noibat", "Oranguru", "Overqwil",
    "Palkia", "Pancham", "Pangoro", "Passimian", "Pawniard", "Phanpy", "Pheromosa", "Pidgey", "Pikipek", "Pinsir",
    "Piplup", "Popplio", "Porygon", "Porygon-Z", "Porygon2", "Primarina", "Prinplup", "Quilava", "Quilladin", "Ralts",
    "Rayquaza", "Regieleki", "Regigigas", "Reshiram", "Rillaboom", "Riolu", "Rockruff", "Rookidee", "Rowlet", "Rufflet",
    "Salakoth", "Salamence", "Sandile", "Sceptile", "Scizor", "Scorbunny", "Scraggy", "Scyther", "Sharpedo", "Shelgon",
    "Shelmet", "Shinx", "Skiddo", "Skorupi", "Skrelp", "Slakoth", "Sliggo", "Sliggoo", "Slowbro", "Slugma",
    "Sneasel", "Sneasler", "Snorlax", "Sobble", "Solgaleo", "Spectrier", "Spritzee", "Squirtle", "Staraptor", "Staravia",
    "Starly", "Staryu", "Steene", "Stoutland", "Swablu", "Swampert", "Swirlix", "Sylveon", "Taillow", "Tauros",
    "Tentacool", "Tepig", "Terrakion", "Thundurus", "Thwackey", "Timburr", "Togekiss", "Togepi", "Togetic", "Torchic",
    "Torterra", "Totodile", "Toxel", "Trapinch", "Treecko", "Turtonator", "Turtwig", "Typhlosion", "Tyranitar", "Tyrantrum",
    "Tyrunt", "Umbreon", "Ursaring", "Urshifu", "Vaporeon", "Venusaur", "Vespiqueen", "Victini", "Vigoroth", "Virizion",
    "Voltorb", "Vullaby", "Vulpix", "Wartortle", "Wimpod", "Wishiwashi", "Xerneas", "Yamper", "Yveltal", "Zacian",
    "Zamazenta", "Zekrom", "Zeraora", "Zoroark", "Zorua", "Zygarde"
]

def get_wait_time():
    """Generates a randomized wait time before clicking buttons."""
    return round(random.uniform(1.2, 1.8), 2)

def get_target_ball_keywords():
    global current_wild_pokemon
    if current_wild_pokemon in repeat_ball:
        return ["repeat ball", "repeat"], "Repeat Ball"
    return ["ultra ball", "ultra"], "Ultra Ball"

async def resolve_target_bot():
    global target_bot_entity
    try:
        target_bot_entity = await client.get_input_entity(target_bot)
        print(f"[LOG] ✅ Target bot entity resolved successfully!")
    except Exception as e:
        print(f"[LOG] ⚠️ Could not resolve target bot entity by ID ({e}). Using fallback ID...")
        target_bot_entity = target_bot

async def send_hunt_command():
    global last_hunt_sent_time, waiting_for_hunt_response, target_bot_entity
    async with hunt_lock:
        if is_in_battle:
            return
        last_hunt_sent_time = asyncio.get_event_loop().time()
        waiting_for_hunt_response = True
        print(f"[LOG] 📤 Sending /hunt to bot {target_bot}...")
        try:
            entity = target_bot_entity if target_bot_entity is not None else target_bot
            await client.send_message(entity, '/hunt')
        except Exception as e:
            print(f"[LOG] ⚠️ Error sending /hunt ({e}). Re-resolving entity...")
            try:
                target_bot_entity = await client.get_input_entity(target_bot)
                await client.send_message(target_bot_entity, '/hunt')
            except Exception as e2:
                print(f"[LOG] ⚠️ Fallback send_message failed: {e2}")

async def response_watchdog():
    global last_hunt_sent_time, waiting_for_hunt_response, is_in_battle
    while True:
        await asyncio.sleep(1.0)
        if waiting_for_hunt_response and not is_in_battle:
            now = asyncio.get_event_loop().time()
            if now - last_hunt_sent_time >= 5.0:
                print(f"[LOG] ⚠️ Bot {target_bot} did not respond within 5s. Resending /hunt...")
                await send_hunt_command()

@client.on(events.NewMessage(from_users=target_bot))
@client.on(events.MessageEdited(from_users=target_bot))
async def global_response_listener(event):
    global waiting_for_hunt_response, target_bot_entity
    waiting_for_hunt_response = False
    if event.input_sender:
        target_bot_entity = event.input_sender

async def find_and_click_button(event, target_keywords):
    if not event.buttons:
        return False
    if isinstance(target_keywords, str):
        target_keywords = [target_keywords]
        
    for row_idx, row in enumerate(event.buttons):
        for col_idx, button in enumerate(row):
            if button.text:
                btn_text_lower = button.text.lower()
                for keyword in target_keywords:
                    if keyword.lower() in btn_text_lower:
                        print(f"[LOG] 🔘 Found button '{button.text}' at ({row_idx}, {col_idx}). Clicking button...")
                        try:
                            await button.click()
                            return True
                        except Exception as e:
                            print(f"[LOG] ⚠️ Error clicking button object '{button.text}': {e}")
                            try:
                                await event.click(row_idx, col_idx)
                                return True
                            except Exception as e2:
                                print(f"[LOG] ⚠️ Fallback index click failed: {e2}")
                                return False
    return False

async def click_button_by_index(event, row_idx=0, col_idx=0):
    if event.buttons and len(event.buttons) > row_idx and len(event.buttons[row_idx]) > col_idx:
        button = event.buttons[row_idx][col_idx]
        print(f"[LOG] 🔘 Clicking button at index ({row_idx}, {col_idx}) -> '{button.text}'")
        try:
            await button.click()
            return True
        except Exception:
            await event.click(row_idx, col_idx)
            return True
    else:
        print(f"[LOG] 🔘 Clicking fallback position ({row_idx}, {col_idx})") # Sahi indentation
        await event.click(row_idx, col_idx)
        return True

def extract_wild_pokemon_info(text):
    name_match = re.search(r"Wild\s+([A-Za-z0-9\-\.\s]+?)(?=\s*\[|\s*\n|\s*Lv)", text)
    hp_match = re.search(r"HP\s*(\d+)\s*/\s*(\d+)", text)
    
    pok_name = name_match.group(1).strip() if name_match else None
    
    if hp_match:
        current_hp = int(hp_match.group(1))
        max_hp = int(hp_match.group(2))
        percentage = round((current_hp / max_hp) * 100) if max_hp > 0 else 0
        return pok_name, current_hp, max_hp, percentage
    return pok_name, None, None, None

@client.on(events.NewMessage(from_users=target_bot))
async def dailyLimit(event):
    if "Daily hunt limit reached" in event.raw_text:
        print("[LOG] 🛑 Daily hunt limit reached! Disconnecting client...")
        await client.disconnect()

@client.on(events.NewMessage(from_users=target_bot))
@client.on(events.MessageEdited(from_users=target_bot))
async def pokeSwitch(event):
    text_lower = event.raw_text.lower()
    if any(k in text_lower for k in ["choose your next pokemon", "choose your next"]):
        global is_in_battle
        is_in_battle = True
        wait_time = get_wait_time()
        print(f"[LOG] 🔄 'Choose your next Pokemon' detected! Waiting {wait_time}s before clicking index (0, 0)...")
        await asyncio.sleep(wait_time)
        await click_button_by_index(event, 0, 0)

@client.on(events.NewMessage(from_users=target_bot))
@client.on(events.MessageEdited(from_users=target_bot))
async def ball_selection_handler(event):
    target_keywords, ball_name = get_target_ball_keywords()
    
    has_target_ball = False
    if event.buttons:
        for row in event.buttons:
            for btn in row:
                if btn.text and any(k in btn.text.lower() for k in target_keywords):
                    has_target_ball = True
                    break
            if has_target_ball:
                break
                
    if has_target_ball:
        global is_in_battle
        is_in_battle = True
        wait_time = get_wait_time()
        print(f"[LOG] 🔴 Ball Selection Screen detected ('{ball_name}' visible). Waiting {wait_time}s before clicking {ball_name}...")
        await asyncio.sleep(wait_time)
        clicked = await find_and_click_button(event, target_keywords)
        if not clicked:
            print(f"[LOG] 🔴 '{ball_name}' click fallback to index (0, 0)...")
            await click_button_by_index(event, 0, 0)

@client.on(events.NewMessage(from_users=target_bot))
async def hunt_or_pass(event):
    global is_in_battle, current_wild_pokemon
    text = event.raw_text
    if "✨ Shiny Pokémon found!" in text:
        print("[LOG] ✨ Shiny Pokémon found! Disconnecting client...")
        await client.disconnect()
    elif "A wild" in text and "HP" not in text:
        try:
            pok_name = text.split("wild ")[1].split(" (")[0].split("!")[0].strip()
        except Exception:
            pok_name = "Unknown"
            
        current_wild_pokemon = pok_name
        print(f"[LOG] 🌲 Response received from bot! Wild Pokémon appeared: '{pok_name}'")
        wait_time = get_wait_time()
        if pok_name in ultra_ball or pok_name in repeat_ball:
            print(f"[LOG] 🎯 '{pok_name}' found in target list. Waiting {wait_time}s before clicking 'Catch'...")
            is_in_battle = True
            await asyncio.sleep(wait_time)
            success = await find_and_click_button(event, ["catch"])
            if not success:
                print(f"[LOG] 🔘 'Catch' button not found by text, clicking fallback index (0, 0)...")
                await click_button_by_index(event, 0, 0)
        else:
            print(f"[LOG] ⏭️ '{pok_name}' not in catch list. Waiting {wait_time}s before sending /hunt...")
            is_in_battle = False
            await asyncio.sleep(wait_time)
            await send_hunt_command()

@client.on(events.MessageEdited(from_users=target_bot))
async def battle_handler(event):
    global is_in_battle, current_wild_pokemon
    text = event.raw_text
    
    finish_keywords = ["ran away safely", "you earned", "fled", "you caught", "caught", "💵"]
    if "Wild" in text and "HP" in text and not any(sub in text.lower() for sub in finish_keywords):
        is_in_battle = True
        pok_name, wild_curr_hp, wild_max_hp, hp_pct = extract_wild_pokemon_info(text)
        if pok_name:
            current_wild_pokemon = pok_name
            
        if wild_curr_hp is None or wild_max_hp is None:
            return
            
        print(f"[LOG] ⚔️ Battle Response Received | Opponent: {pok_name if pok_name else 'Wild'} | HP: {wild_curr_hp}/{wild_max_hp} ({hp_pct}%)")
        
        has_false_swipe = False
        if "false swipe" in text.lower():
            has_false_swipe = True
        elif event.buttons:
            for row in event.buttons:
                for btn in row:
                    if btn.text and "false swipe" in btn.text.lower():
                        has_false_swipe = True
                        break
        
        print(f"[LOG] 🔍 Checking moves... False Swipe Available: {has_false_swipe}")
        
        req_met = (wild_curr_hp <= 1) if has_false_swipe else (hp_pct <= 40)
        wait_time = get_wait_time()
        
        if req_met:
            target_keywords, ball_name = get_target_ball_keywords()
            print(f"[LOG] 🎯 Catch requirement met! (False Swipe: {has_false_swipe}, HP: {wild_curr_hp}/{wild_max_hp} [{hp_pct}%]). Selected Ball: {ball_name}")
            
            ball_clicked = False
            if event.buttons:
                for row in event.buttons:
                    for btn in row:
                        if btn.text and any(k in btn.text.lower() for k in target_keywords):
                            ball_clicked = True
                            break
                    if ball_clicked:
                        break
            
            if ball_clicked:
                print(f"[LOG] 🔴 '{ball_name}' visible directly. Waiting {wait_time}s before clicking '{ball_name}'...")
                await asyncio.sleep(wait_time)
                await find_and_click_button(event, target_keywords)
                return
                
            print(f"[LOG] 📦 Opening ball menu. Waiting {wait_time}s before clicking 'Poke Ball'...")
            await asyncio.sleep(wait_time)
            poke_ball_clicked = await find_and_click_button(event, ["poke ball", "poke balls", "ball"])
            if not poke_ball_clicked:
                print(f"[LOG] ⚠️ 'Poke Ball' button not found directly.")
        else:
            if has_false_swipe:
                print(f"[LOG] ⚔️ Requirement not met (Target HP <= 1). Waiting {wait_time}s before using move 'False Swipe'...")
                await asyncio.sleep(wait_time)
                clicked = await find_and_click_button(event, ["false swipe"])
                if not clicked:
                    print(f"[LOG] ⚔️ 'False Swipe' button click fallback to index (0, 0)...")
                    await click_button_by_index(event, 0, 0)
            else:
                print(f"[LOG] ⚔️ Requirement not met (Target HP <= 40%). 'False Swipe' not available. Waiting {wait_time}s before using move at Index 0...")
                await asyncio.sleep(wait_time)
                await click_button_by_index(event, 0, 0)

@client.on(events.NewMessage(from_users=target_bot))
async def skip(event):
    global is_in_battle
    text = event.raw_text
    finish_keywords = ["ran away safely", "you earned", "fled", "you caught", "caught", "💵"]
    if any(keyword in text.lower() for keyword in finish_keywords):
        is_in_battle = False
        wait_time = get_wait_time()
        print(f"[LOG] 🏁 Battle ended / finish response received ('{text.strip().replace(chr(10), ' ')}'). Waiting {wait_time}s before sending next /hunt...")
        await asyncio.sleep(wait_time)
        await send_hunt_command()

@client.on(events.NewMessage(from_users=target_bot))
async def skipTrainer(event):
    global is_in_battle
    if "An expert trainer" in event.raw_text:
        is_in_battle = False
        wait_time = get_wait_time()
        print(f"[LOG] ⚠️ Expert trainer response received! Waiting {wait_time}s before sending next /hunt...")
        await asyncio.sleep(wait_time)
        await send_hunt_command()

async def main():
    await client.start()
    print(f"[LOG] 🚀 Telegram Client started targeting Bot ID: {target_bot}")
    
    try:
        await client.get_dialogs(limit=50)
    except Exception:
        pass
        
    await resolve_target_bot()
    asyncio.create_task(response_watchdog())
    await send_hunt_command()
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())

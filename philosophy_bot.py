"""
Philosophy Discord Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Auto-reageert in channel 1505313262860894308 met:
  "If [concept] is your power, what are you without it?"

App Commands (rechtermuisklik op bericht → Apps):
  • Philosophize        → stuurt de vraag als reply in het kanaal
  • Philosophize → DM   → stuurt de vraag privé naar jou
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os

import discord
from discord import app_commands
import re
from collections import Counter

# ──────────────────────────────────────────────
# CONFIG  ← vul dit in
# ──────────────────────────────────────────────
TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL_ID = 1505313262860894308

# Optioneel: je server ID voor instant command-sync tijdens development.
# Laat None voor global commands (duurt ~1 uur om te verschijnen).
GUILD_ID = None  # Bijv: 123456789012345678

# ──────────────────────────────────────────────
# KEYWORD EXTRACTIE (zonder AI)
# ──────────────────────────────────────────────

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "you", "your", "he", "she", "it",
    "they", "them", "this", "that", "the", "a", "an", "and", "or", "but",
    "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "just", "so",
    "not", "no", "if", "then", "than", "too", "very", "also", "like", "as",
    "what", "who", "how", "when", "where", "why", "which", "from", "about",
    "up", "out", "into", "through", "by", "more", "some", "any", "all",
    "ik", "je", "jij", "we", "zij", "hij", "de", "het", "een", "en", "of",
    "maar", "in", "op", "aan", "voor", "van", "met", "is", "zijn", "was",
    "dat", "dit", "zich", "om", "te", "er", "al", "nog", "wel", "niet",
    "im", "its", "dont", "cant", "wont", "ive", "youre", "theyre",
    "s", "t", "m", "re", "ll", "ve", "d",
}

CONCEPT_MAP = {
    "money": "money", "wealth": "wealth", "rich": "wealth", "broke": "money",
    "fame": "fame", "popular": "popularity", "followers": "followers",
    "likes": "validation", "views": "attention", "clout": "clout",
    "success": "success", "winning": "winning", "losing": "failure",
    "power": "power", "control": "control", "strength": "strength",
    "beauty": "beauty", "looks": "your looks", "attractive": "attraction",
    "smart": "intelligence", "intelligent": "intelligence", "genius": "genius",
    "talent": "talent", "skill": "skill", "ability": "ability",
    "job": "your job", "work": "work", "career": "career", "boss": "authority",
    "title": "your title", "position": "your position", "rank": "rank",
    "friend": "your friends", "friends": "your friends", "friendship": "friendship",
    "love": "love", "relationship": "your relationship", "partner": "your partner",
    "family": "family", "parents": "your parents", "mother": "your mother",
    "father": "your father", "brother": "your brother", "sister": "your sister",
    "happy": "happiness", "happiness": "happiness", "joy": "joy",
    "sad": "sadness", "pain": "pain", "hurt": "your pain",
    "angry": "your anger", "anger": "anger", "hate": "hate",
    "fear": "fear", "anxiety": "anxiety", "stress": "stress",
    "confidence": "confidence", "ego": "your ego", "pride": "pride",
    "shame": "shame", "guilt": "guilt",
    "music": "music", "art": "art", "creativity": "creativity",
    "writing": "writing", "words": "your words", "voice": "your voice",
    "education": "education", "degree": "your degree", "school": "school",
    "knowledge": "knowledge", "wisdom": "wisdom", "truth": "truth",
    "god": "faith", "faith": "faith", "religion": "religion", "belief": "belief",
    "body": "your body", "health": "health", "fit": "fitness", "gym": "the gym",
    "food": "food", "sleep": "sleep", "rest": "rest",
    "time": "time", "age": "age", "youth": "youth", "old": "age",
    "social media": "social media", "instagram": "social media",
    "tiktok": "social media", "twitter": "social media", "phone": "your phone",
    "internet": "the internet", "technology": "technology",
    "game": "gaming", "gaming": "gaming", "sport": "sport", "sports": "sport",
    "team": "your team", "player": "being a player",
    "leader": "leadership", "leadership": "leadership",
    "freedom": "freedom", "choice": "choice", "decision": "your decisions",
    "past": "your past", "future": "your future", "memory": "your memories",
    "trauma": "your trauma", "story": "your story", "name": "your name",
    "reputation": "reputation", "image": "your image", "brand": "your brand",
    "race": "race", "gender": "gender", "identity": "identity",
    "culture": "culture", "roots": "your roots", "language": "language",
    "home": "home", "place": "your place", "city": "your city",
    "dream": "your dreams", "goal": "your goals", "ambition": "ambition",
    "hope": "hope", "purpose": "purpose", "meaning": "meaning",
    "life": "life", "death": "death", "existence": "existence",
    "opinion": "your opinions", "ideas": "your ideas", "thoughts": "your thoughts",
    "humor": "humor", "funny": "humor", "laugh": "laughter",
    "attention": "attention", "recognition": "recognition",
    "respect": "respect", "honor": "honor",
    "loneliness": "loneliness", "alone": "being alone", "isolation": "isolation",
    "connection": "connection", "belonging": "belonging",
    "discipline": "discipline", "routine": "your routine", "habit": "your habits",
    "mind": "your mind", "heart": "your heart", "soul": "your soul",
    "privilege": "privilege", "luck": "luck",
    "struggle": "your struggle", "hustle": "the hustle", "nigger": "racism to black people",
    "socrates": "getting ragebaited", "femboys": "gooning to femboys", "femboy": "gooning to femboys",
    "nigga": "racism to black people", "niggers": "racism to black people", "nig": "racism to black people",
    "nga": "racism to black people", "gooning": "gooning", "goon": "gooning", "Geometry Dash": "gooning to femboys", "geometry dash": "gooning to femboys",
    "reference": "Nine Circles", "florr": "not touching grass", "flor": "not touching grass", "florrr": "not touching grass",
    "Cubing_Pro": "math", "cubing_pro": "math", "cubingpro": "math", "cubing_hater": "unemployedness",
    "cubing hater": "unemployedness", "cubinghater": "unemployedness",
    "Marcel Rudge": "your basement", "marcel rudge": "your basement", "marcel": "your basement", "mr": "your basement",
    "fmmr": "your basement", "pong": "youtube", "nya": "being a furry", "furry": "being a furry", "furries": "being a furry",
    "meow": "being a furry", "purr": "being a furry", "cat": "being a furry", "dog": "being a furry",
    "David": "leaking everything", "david": "leaking everything", "davidaa": "leaking everything",
    "Stierstraat 11": "leaking everything", "stierstraat 11": "leaking everything", "stierstraat11": "leaking everything",
    "Moeshie": "cuteness", "moeshie": "cuteness", "moe": "cuteness", "shie": "cuteness", "@core_cyan": "skullbait",
    "core_cyan": "skullbait", "Core_Cyan": "skullbait", "Core_cyan": "skullbait", "core_Cyan": "skullbait",
    "corecyan": "skullbait", "CoreCyan": "skullbait", "corecyan": "skullbait",
    "“You will die in a house fire” said the oracle. I am a shrimp. I live in the ocean. And house fires cannot start in the ocean. Today I left my house to do my shrimpy business, like all shrimps do. When I returned home, I decided to go play some florr.io to relax myself and have some fun. Then I decided to go see the oracle because why not. “You will die in a house fire” said the oracle again. Surely this had to be false. Then I smelt something burning. The smell of smoke only grew bigger. Eventually I decided to check where the smoke was coming from, and guess what? It was coming from my house. Fearing for my life, I decided to escape my house, but all the exits were blocked. How is this possible? House fires cannot start in the ocean, but how did I have one anyway? Was I really going to die? Am I really going to face my worst nightmare? Becoming a fried shrimp?": "being a fried shrimp",
    "house fires cannot start in the ocean": "being a fried shrimp",
    "stole": "stealing", "steal": "stealing", "stole from": "stealing", "stole my": "stealing", "stole your": "stealing", "stole his": "stealing", "stole her": "stealing", "stole their": "stealing", "stole our": "stealing", "stole the": "stealing",

}

VERB_CONCEPTS = {
    "play": "playing", "playing": "playing",
    "run": "running", "running": "running",
    "fight": "fighting", "fighting": "fighting",
    "help": "helping others", "helping": "helping others",
    "create": "creating", "creating": "creating",
    "build": "building", "building": "building",
    "lead": "leading", "leading": "leading",
    "teach": "teaching", "teaching": "teaching",
    "learn": "learning", "learning": "learning",
    "perform": "performing", "performing": "performing",
    "compete": "competing", "competing": "competing",
    "win": "winning", "winning": "winning",
    "lose": "losing", "losing": "losing",
    "talk": "talking", "talking": "talking",
    "listen": "listening", "listening": "listening",
    "give": "giving", "giving": "giving",
    "take": "taking", "taking": "taking",
    "show": "showing off", "showing": "showing off",
    "control": "control", "controlling": "control",
    "protect": "protecting", "protecting": "protecting",
}


def extract_power(message_text: str) -> str:
    text = message_text.lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s']", " ", text)
    words = text.split()

    for length in [3, 2, 1]:
        for i in range(len(words) - length + 1):
            phrase = " ".join(words[i:i+length])
            if phrase in CONCEPT_MAP:
                return CONCEPT_MAP[phrase]

    for word in words:
        if word in VERB_CONCEPTS:
            return VERB_CONCEPTS[word]

    candidates = [w for w in words if w not in STOPWORDS and len(w) >= 4 and w.isalpha()]
    if candidates:
        freq = Counter(candidates)
        return max(candidates, key=lambda w: (freq[w], len(w)))

    fallbacks = [
        "what you know", "what you have", "what others think of you",
        "your past", "your image", "your certainty",
    ]
    return fallbacks[len(message_text) % len(fallbacks)]


def build_question(power: str) -> str:
    return f"If **{power}** is your power, what are you without it?"


# ──────────────────────────────────────────────
# BOT SETUP
# ──────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

guild_obj = discord.Object(id=GUILD_ID) if GUILD_ID else None


# ──────────────────────────────────────────────
# APP COMMANDS  (rechtermuisklik → Apps)
# ──────────────────────────────────────────────

@tree.context_menu(name="Philosophize")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def philosophize_public(
    interaction: discord.Interaction,
    message: discord.Message,
):
    content = message.content.strip()

    if not content:
        await interaction.response.send_message(
            "❌ This message has no text to analyze.",
            ephemeral=True,
        )
        return

    power = extract_power(content)
    question = build_question(power)

    await interaction.response.send_message(question)


@tree.context_menu(name="Philosophize → DM")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def philosophize_dm(
    interaction: discord.Interaction,
    message: discord.Message,
):
    """Sends the philosophical question to the user's DMs."""
    content = message.content.strip()

    if not content:
        await interaction.response.send_message(
            "❌ This message has no text to analyze.",
            ephemeral=True,
        )
        return

    power = extract_power(content)
    question = build_question(power)

    try:
        await interaction.user.send(
            f"**Philosophical question about a message from {message.author.display_name}:**\n"
            f"> {message.content[:200]}\n\n"
            f"{question}"
        )
        await interaction.response.send_message("📬 Check your DMs!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I can't send you a DM. Please enable DMs for this server.",
            ephemeral=True,
        )


# ──────────────────────────────────────────────
# EVENTS
# ──────────────────────────────────────────────

@client.event
async def on_ready():
        await tree.sync()
        print(f"⚡ Commands gesync (instant)")
        if guild_obj:
            await tree.sync(guild=guild_obj)
            print(f"⚡ Commands gesync naar guild {GUILD_ID}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    content = message.content.strip()
    if not content:
        return

    power = extract_power(content)
    question = build_question(power)
    await message.reply(question, mention_author=False)

@tree.command(name="philosophize", description="Socrates will philosophize about your concept")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def philosophize_slash(interaction: discord.Interaction, tekst: str):
    power = extract_power(tekst)
    question = build_question(power)
    await interaction.response.send_message(question)


# ──────────────────────────────────────────────
# START
# ──────────────────────────────────────────────
if __name__ == "__main__":
    if TOKEN == "JOUW_BOT_TOKEN_HIER":
        print("❌ Vul je bot token in bij TOKEN!")
    else:
        client.run(TOKEN)
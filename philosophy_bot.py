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
    "suiko": "blood",
    
    "verified": "being verified", "checkmark": "your checkmark",
    "subscribers": "your subscribers", "subscribers": "your audience",
    "retweets": "attention", "shares": "your reach", "viral": "going viral",
    "influencer": "your influence", "content": "your content",
    "creator": "being a creator", "streamer": "streaming",
    "platform": "your platform", "algorithm": "the algorithm",
    "engagement": "engagement", "analytics": "your numbers",
    "monetize": "monetization", "sponsorship": "sponsorships",
    "collab": "collaboration", "network": "your network",
    "exposure": "exposure", "branding": "your brand",
    "aesthetic": "your aesthetic", "feed": "your feed",
    "highlight": "your highlights", "story": "your story",
    "niche": "your niche", "audience": "your audience",
    "comment": "your comments", "reply": "your replies",
    "notification": "notifications", "badge": "your badge",

    "salary": "your salary", "income": "income", "debt": "your debt",
    "loan": "loans", "credit": "credit", "savings": "your savings",
    "investment": "investments", "stock": "stocks", "crypto": "crypto",
    "bitcoin": "bitcoin", "nft": "NFTs", "asset": "your assets",
    "property": "property", "house": "your house", "car": "your car",
    "luxury": "luxury", "designer": "designer labels", "brand": "your brand",
    "expensive": "expensive things", "cheap": "being cheap",
    "profit": "profit", "loss": "your losses", "budget": "your budget",
    "tip": "tips", "bonus": "your bonus", "raise": "your raise",
    "promotion": "your promotion", "contract": "your contract",

    "ex": "your ex", "crush": "your crush", "date": "dating",
    "marriage": "marriage", "divorce": "divorce", "single": "being single",
    "loyalty": "loyalty", "betrayal": "betrayal", "trust": "trust",
    "jealousy": "jealousy", "envy": "envy", "gossip": "gossip",
    "drama": "drama", "conflict": "conflict", "argument": "your arguments",
    "apology": "your apologies", "forgiveness": "forgiveness",
    "boundary": "your boundaries", "toxic": "toxicity",
    "support": "support", "validation": "validation", "approval": "approval",
    "rejection": "rejection", "acceptance": "acceptance",
    "community": "community", "tribe": "your tribe",
    "crowd": "the crowd", "popularity": "popularity",
    "social": "your social life", "networking": "networking",
    "mentorship": "mentorship", "mentor": "your mentor",
    "influence": "your influence", "peer": "your peers",
    "competition": "competition", "rivalry": "rivalry",
    "enemy": "your enemies", "hater": "your haters", "fan": "your fans",
    "follower": "your followers", "idol": "your idols",

    "honesty": "honesty", "integrity": "integrity", "loyalty": "loyalty",
    "courage": "courage", "bravery": "bravery", "coward": "cowardice",
    "kindness": "kindness", "compassion": "compassion", "empathy": "empathy",
    "patience": "patience", "gratitude": "gratitude", "humility": "humility",
    "arrogance": "arrogance", "narcissism": "narcissism",
    "insecurity": "your insecurities", "doubt": "your doubts",
    "overthinking": "overthinking", "worry": "your worries",
    "regret": "regret", "nostalgia": "nostalgia", "bitterness": "bitterness",
    "resilience": "resilience", "persistence": "persistence",
    "determination": "determination", "willpower": "willpower",
    "motivation": "motivation", "inspiration": "inspiration",
    "creativity": "creativity", "curiosity": "curiosity",
    "passion": "passion", "obsession": "obsession",
    "addiction": "addiction", "habit": "your habits",
    "routine": "your routine", "comfort": "comfort",
    "vulnerability": "vulnerability", "authenticity": "authenticity",
    "charisma": "charisma", "charm": "charm", "wit": "wit",
    "sarcasm": "sarcasm", "irony": "irony",

    "weight": "your weight", "diet": "your diet", "calories": "calories",
    "muscle": "muscle", "fat": "body fat", "skinny": "being skinny",
    "workout": "working out", "exercise": "exercise", "cardio": "cardio",
    "running": "running", "lifting": "lifting", "yoga": "yoga",
    "meditation": "meditation", "breathing": "your breathing",
    "sobriety": "sobriety", "drugs": "drugs", "alcohol": "alcohol",
    "smoking": "smoking", "drinking": "drinking",
    "therapy": "therapy", "healing": "healing", "recovery": "recovery",
    "sickness": "sickness", "illness": "illness", "disability": "disability",
    "surgery": "surgery", "medication": "medication",
    "mental health": "mental health", "depression": "depression",
    "self-worth": "self-worth", "self-love": "self-love",
    "self-care": "self-care", "burnout": "burnout",
    "exhaustion": "exhaustion", "energy": "your energy",
    "adrenaline": "adrenaline", "dopamine": "dopamine",

    "grades": "your grades", "gpa": "your GPA", "exam": "exams",
    "test": "tests", "diploma": "your diploma", "certificate": "certificates",
    "award": "awards", "trophy": "trophies", "medal": "medals",
    "record": "your record", "achievement": "achievements",
    "milestone": "milestones", "progress": "progress", "growth": "growth",
    "improvement": "improvement", "potential": "your potential",
    "opportunity": "opportunity", "chance": "your chances",
    "risk": "risk", "gamble": "gambling", "bet": "your bets",
    "plan": "your plans", "strategy": "strategy", "vision": "your vision",
    "mission": "your mission", "legacy": "your legacy",
    "impact": "impact", "contribution": "your contribution",
    "change": "change", "revolution": "revolution", "movement": "the movement",

    "morality": "morality", "ethics": "ethics", "justice": "justice",
    "fairness": "fairness", "equality": "equality", "privilege": "privilege",
    "suffering": "suffering", "sacrifice": "sacrifice", "loss": "loss",
    "grief": "grief", "emptiness": "emptiness", "void": "the void",
    "silence": "silence", "darkness": "darkness", "light": "light",
    "shadow": "your shadow", "reflection": "your reflection",
    "perception": "perception", "reality": "reality", "illusion": "illusion",
    "ego": "your ego", "soul": "your soul", "spirit": "your spirit",
    "karma": "karma", "fate": "fate", "destiny": "destiny",
    "luck": "luck", "coincidence": "coincidence", "universe": "the universe",
    "universe": "the universe", "chaos": "chaos", "order": "order",
    "balance": "balance", "harmony": "harmony", "peace": "peace",
    "war": "war", "violence": "violence", "anger": "anger",
    "revolution": "revolution", "system": "the system",
    "structure": "structure", "rule": "rules", "law": "the law",
    "authority": "authority", "obedience": "obedience", "rebellion": "rebellion",
    "conformity": "conformity", "individuality": "individuality",
    "originality": "originality", "uniqueness": "being unique",
    "normality": "normality", "weirdness": "your weirdness",

    "score": "the score", "rank": "your rank", "rating": "your rating",
    "level": "your level", "tier": "your tier", "league": "your league",
    "championship": "the championship", "title": "your title",
    "draft": "the draft", "contract": "your contract",
    "stats": "your stats", "performance": "performance",
    "training": "training", "practice": "practice", "coach": "your coach",
    "captain": "being captain", "starter": "being a starter",
    "bench": "the bench", "substitute": "being a substitute",
    "underdog": "being the underdog", "favorite": "being the favorite",
    "comeback": "the comeback", "defeat": "defeat", "victory": "victory",

    "startup": "your startup", "business": "your business",
    "entrepreneur": "entrepreneurship", "hustle": "the hustle",
    "grind": "the grind", "side hustle": "your side hustle",
    "passive income": "passive income", "freelance": "freelancing",
    "remote": "remote work", "office": "the office",
    "meeting": "meetings", "deadline": "deadlines", "project": "your project",
    "client": "your clients", "customer": "your customers",
    "product": "your product", "service": "your service",
    "feedback": "feedback", "review": "reviews", "rating": "your rating",
    "reputation": "reputation", "credibility": "credibility",
    "expertise": "expertise", "experience": "experience",
    "internship": "internships", "interview": "interviews",
    "resume": "your resume", "portfolio": "your portfolio",
    "reference": "references", "recommendation": "recommendations",

    "code": "code", "coding": "coding", "programming": "programming",
    "hacking": "hacking", "software": "software", "hardware": "hardware",
    "data": "data", "ai": "AI slop", "robot": "robots",
    "automation": "automation", "algorithm": "algorithms",
    "minecraft": "Minecraft", "fortnite": "Fortnite", "ranked": "ranked",
    "meta": "the meta", "loadout": "your loadout", "build": "your build",
    "kill": "your kills", "death": "your deaths", "win rate": "your win rate",
    "clutch": "the clutch", "carry": "carrying", "toxic": "toxicity",
    "noob": "being called a noob", "pro": "being a pro",
    "esports": "esports", "tournament": "tournaments",

    "nature": "nature", "earth": "the earth", "ocean": "the ocean",
    "mountain": "the mountain", "forest": "the forest", "fire": "fire",
    "water": "water", "air": "air", "storm": "the storm",
    "sun": "the sun", "moon": "the moon", "stars": "the stars",
    "energy": "energy", "vibration": "your vibration", "frequency": "frequency",
    "manifestation": "manifestation", "law of attraction": "the law of attraction",
    "mindfulness": "mindfulness", "gratitude": "gratitude",
    "chakra": "your chakras", "aura": "your aura",
    "intuition": "intuition", "instinct": "instinct",
    "signs": "signs", "synchronicity": "synchronicity",

    "opinion": "your opinion", "perspective": "your perspective",
    "narrative": "your narrative", "excuse": "your excuses",
    "blame": "blame", "victim": "victimhood", "survivor": "survival",
    "mask": "your mask", "facade": "your facade", "role": "your role",
    "label": "labels", "stereotype": "stereotypes", "assumption": "assumptions",
    "expectation": "expectations", "pressure": "pressure",
    "standard": "standards", "norm": "norms", "tradition": "tradition",
    "change": "change", "growth": "growth", "transformation": "transformation",
    "awakening": "awakening", "realization": "realization",
    "clarity": "clarity", "confusion": "confusion", "uncertainty": "uncertainty",
    "answer": "your answers", "question": "your questions",
    "secret": "your secrets", "lie": "your lies", "truth": "truth",
    "promise": "your promises", "commitment": "commitment",
    "discipline": "discipline", "sacrifice": "sacrifice",
    "obsession": "obsession", "fixation": "fixation",

    "钱": "money", "财富": "wealth", "成功": "success",
    "名声": "fame", "权力": "power", "地位": "status",
    "面子": "face", "荣誉": "honor", "尊重": "respect",
    "家庭": "family", "爱": "love", "友谊": "friendship",
    "朋友": "your friends", "父母": "your parents", "孩子": "your children",
    "健康": "health", "美丽": "beauty", "身体": "your body",
    "工作": "work", "事业": "career", "学历": "your degree",
    "知识": "knowledge", "智慧": "wisdom", "才华": "talent",
    "梦想": "your dreams", "目标": "your goals", "未来": "your future",
    "过去": "your past", "记忆": "your memories", "希望": "hope",
    "自由": "freedom", "选择": "choice", "命运": "destiny",
    "运气": "luck", "机会": "opportunity", "努力": "hard work",
    "坚持": "persistence", "勇气": "courage", "信心": "confidence",
    "骄傲": "pride", "谦虚": "humility", "善良": "kindness",
    "诚实": "honesty", "忠诚": "loyalty", "信任": "trust",
    "嫉妒": "jealousy", "恐惧": "fear", "痛苦": "pain",
    "孤独": "loneliness", "快乐": "happiness", "平静": "peace",
    "意义": "meaning", "目的": "purpose", "灵魂": "your soul",
    "身份": "identity", "文化": "culture", "根": "your roots",
    "语言": "language", "家": "home", "归属感": "belonging",
    "社会": "society", "规则": "rules", "权威": "authority",
    "变化": "change", "成长": "growth", "进步": "progress",
    "创造力": "creativity", "艺术": "art", "音乐": "music",
    "时间": "time", "年龄": "age", "死亡": "death",
    "生命": "life", "存在": "existence", "真相": "truth",
    "道德": "morality", "正义": "justice", "平等": "equality",
    "牺牲": "sacrifice", "奉献": "dedication", "责任": "responsibility",
    "压力": "pressure", "期望": "expectations", "标准": "standards",
    "完美": "perfection", "失败": "failure", "胜利": "victory",
    "竞争": "competition", "成就": "achievement", "荣耀": "glory",
    "影响力": "influence", "领导力": "leadership", "团队": "your team",
    "控制": "control", "力量": "strength", "意志力": "willpower",
    "激情": "passion", "执着": "obsession", "习惯": "your habits",
    "纪律": "discipline", "自律": "self-discipline", "自我": "your ego",
    "内心": "your inner self", "价值观": "your values",

    "geld": "money", "rijkdom": "wealth", "succes": "success",
    "roem": "fame", "macht": "power", "status": "status",
    "eer": "honor", "respect": "respect", "waardigheid": "dignity",
    "familie": "family", "liefde": "love", "vriendschap": "friendship",
    "vrienden": "your friends", "ouders": "your parents", "kinderen": "your children",
    "gezondheid": "health", "schoonheid": "beauty", "lichaam": "your body",
    "werk": "work", "carrière": "career", "opleiding": "your education",
    "kennis": "knowledge", "wijsheid": "wisdom", "talent": "talent",
    "dromen": "your dreams", "doelen": "your goals", "toekomst": "your future",
    "verleden": "your past", "herinneringen": "your memories", "hoop": "hope",
    "vrijheid": "freedom", "keuze": "choice", "lot": "destiny",
    "geluk": "luck", "kans": "opportunity", "doorzettingsvermogen": "persistence",
    "moed": "courage", "zelfvertrouwen": "confidence", "trots": "pride",
    "bescheidenheid": "humility", "vriendelijkheid": "kindness",
    "eerlijkheid": "honesty", "loyaliteit": "loyalty", "vertrouwen": "trust",
    "jaloezie": "jealousy", "angst": "fear", "pijn": "pain",
    "eenzaamheid": "loneliness", "geluk": "happiness", "rust": "peace",
    "betekenis": "meaning", "doel": "purpose", "ziel": "your soul",
    "identiteit": "identity", "cultuur": "culture", "wortels": "your roots",
    "taal": "language", "thuis": "home", "verbondenheid": "belonging",
    "samenleving": "society", "regels": "rules", "autoriteit": "authority",
    "verandering": "change", "groei": "growth", "vooruitgang": "progress",
    "creativiteit": "creativity", "kunst": "art", "muziek": "music",
    "tijd": "time", "leeftijd": "age", "dood": "death",
    "leven": "life", "bestaan": "existence", "waarheid": "truth",
    "moraliteit": "morality", "rechtvaardigheid": "justice", "gelijkheid": "equality",
    "opoffering": "sacrifice", "toewijding": "dedication", "verantwoordelijkheid": "responsibility",
    "druk": "pressure", "verwachtingen": "expectations", "normen": "standards",
    "perfectie": "perfection", "mislukking": "failure", "overwinning": "victory",
    "concurrentie": "competition", "prestatie": "achievement", "glorie": "glory",
    "invloed": "influence", "leiderschap": "leadership", "team": "your team",
    "controle": "control", "kracht": "strength", "wilskracht": "willpower",
    "passie": "passion", "obsessie": "obsession", "gewoonten": "your habits",
    "discipline": "discipline", "ego": "your ego", "zelfbeeld": "your self-image",
    "waarden": "your values", "karakter": "character",

    "dinero": "money", "riqueza": "wealth", "éxito": "success",
    "fama": "fame", "poder": "power", "estatus": "status",
    "honor": "honor", "respeto": "respect", "dignidad": "dignity",
    "familia": "family", "amor": "love", "amistad": "friendship",
    "amigos": "your friends", "padres": "your parents", "hijos": "your children",
    "salud": "health", "belleza": "beauty", "cuerpo": "your body",
    "trabajo": "work", "carrera": "career", "educación": "your education",
    "conocimiento": "knowledge", "sabiduría": "wisdom", "talento": "talent",
    "sueños": "your dreams", "metas": "your goals", "futuro": "your future",
    "pasado": "your past", "recuerdos": "your memories", "esperanza": "hope",
    "libertad": "freedom", "elección": "choice", "destino": "destiny",
    "suerte": "luck", "oportunidad": "opportunity", "persistencia": "persistence",
    "valentía": "courage", "confianza": "confidence", "orgullo": "pride",
    "humildad": "humility", "bondad": "kindness", "honestidad": "honesty",
    "lealtad": "loyalty", "confianza": "trust", "celos": "jealousy",
    "miedo": "fear", "dolor": "pain", "soledad": "loneliness",
    "felicidad": "happiness", "paz": "peace", "significado": "meaning",
    "propósito": "purpose", "alma": "your soul", "identidad": "identity",
    "cultura": "culture", "raíces": "your roots", "idioma": "language",
    "hogar": "home", "pertenencia": "belonging", "sociedad": "society",
    "reglas": "rules", "autoridad": "authority", "cambio": "change",
    "crecimiento": "growth", "progreso": "progress", "creatividad": "creativity",
    "arte": "art", "música": "music", "tiempo": "time",
    "edad": "age", "muerte": "death", "vida": "life",
    "existencia": "existence", "verdad": "truth", "moralidad": "morality",
    "justicia": "justice", "igualdad": "equality", "sacrificio": "sacrifice",
    "dedicación": "dedication", "responsabilidad": "responsibility",
    "presión": "pressure", "expectativas": "expectations", "estándares": "standards",
    "perfección": "perfection", "fracaso": "failure", "victoria": "victory",
    "competencia": "competition", "logro": "achievement", "gloria": "glory",
    "influencia": "influence", "liderazgo": "leadership", "equipo": "your team",
    "control": "control", "fuerza": "strength", "fuerza de voluntad": "willpower",
    "pasión": "passion", "obsesión": "obsession", "hábitos": "your habits",
    "disciplina": "discipline", "ego": "your ego", "valores": "your values",
    "carácter": "character", "reputación": "reputation",
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

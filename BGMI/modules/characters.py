from BGMI import bot 
from pyrogram import filters
from pyrogram.types import Message



# Character and Enemy Data
character_data = {
    "Carlo": {
        "hp": "100",
        "photo": "https://files.catbox.moe/44rxqs.jpg",
        "caption": "Goku is a Saiyan warrior known for his incredible strength and determination to protect Earth.",
        "base_stats": {"hp": 100, "atk": 50, "def": 50, "spe": 40, "acc": 88},
        "weapons": {
            "fist": {"damage": [10, 20], "level": 1},
            "Spirit Bomb": {"damage": [60, 80], "level": 20},
            "Super Saiyan Rush": {"damage": [80, 100], "level": 60},
            "Ultra Instinct Strike": {"damage": [100, 120], "level": 100}
        }
    },
    "Sarah": {
        "hp": "100",
        "photo": "https://files.catbox.moe/w67puk.jpg",
        "caption": "Vegeta is the Prince of Saiyans, known for his pride and relentless drive to surpass Goku.",
        "base_stats": {"hp": 100, "atk": 50, "def": 50, "spe": 40, "acc": 87},
        "weapons": {
            "fist": {"damage": [10, 20], "level": 1},
            "Big Bang Attack": {"damage": [60, 80], "level": 20},
            "Final Flash": {"damage": [80, 100], "level": 60},
            "Super Saiyan Blue Evolution Strike": {"damage": [100, 120], "level": 100}
        }
    },
    "Andy": {
        "hp": "250",
        "photo": "https://files.catbox.moe/j6fbyp.jpg",
        "caption": "Piccolo is a Namekian warrior known for his intelligence, regeneration, and powerful techniques.",
        "base_stats": {"hp": 250, "atk": 78, "def": 82, "spe": 75, "acc": 80},
        "moves": {
            "Special Beam Cannon": {"damage": [20, 50], "level": 1},
            "Hellzone Grenade": {"damage": [50, 70], "level": 20},
            "Explosive Wave": {"damage": [70, 90], "level": 60},
            "Namekian Fury": {"damage": [90, 110], "level": 100}
        }
    },
    "Marshel": {
        "hp": "275",
        "photo": "https://files.catbox.moe/n6vkte.jpg",
        "caption": "Gohan is the hybrid Saiyan son of Goku, known for his potential and transformation into Ultimate Gohan.",
        "base_stats": {"hp": 275, "atk": 84, "def": 78, "spe": 82, "acc": 85},
        "moves": {
            "Masenko": {"damage": [20, 50], "level": 1},
            "Super Kamehameha": {"damage": [50, 70], "level": 20},
            "Mystic Strike": {"damage": [70, 90], "level": 60},
            "Ultimate Fury": {"damage": [90, 110], "level": 100}
        }
    },
    "Victor": {
        "hp": "240",
        "photo": "https://files.catbox.moe/ycnuph.jpg",
        "caption": "Krillin is a loyal Earthling warrior known for his bravery and advanced martial arts skills.",
        "base_stats": {"hp": 240, "atk": 72, "def": 68, "spe": 78, "acc": 82},
        "moves": {
            "Destructo Disk": {"damage": [20, 50], "level": 1},
            "Solar Flare": {"damage": [50, 65], "level": 20},
            "Triple Energy Wave": {"damage": [65, 80], "level": 60},
            "Max Power Kamehameha": {"damage": [80, 100], "level": 100}
        }
    },
    "Dr Drillin": {
        "hp": "230",
        "photo": "https://files.catbox.moe/1hve7t.jpg",
        "caption": "Cabba is a Saiyan from Universe 6, known for his politeness and quick mastery of Super Saiyan.",
        "base_stats": {"hp": 230, "atk": 76, "def": 70, "spe": 80, "acc": 79},
        "moves": {
            "Saiyan Charge": {"damage": [20, 45], "level": 1},
            "Galick Cannon": {"damage": [45, 70], "level": 20},
            "Super Saiyan Burst": {"damage": [70, 100], "level": 60},
            "Universe 6 Fury": {"damage": [100, 110], "level": 100}
        }
    },
    "Smag": {
        "hp": "250",
        "photo": "https://files.catbox.moe/4xpygh.jpg",
        "caption": "Tien is a disciplined martial artist who excels in advanced techniques and has a strong sense of justice.",
        "base_stats": {"hp": 250, "atk": 78, "def": 75, "spe": 77,"acc": 80},
        "moves": {
            "Tri-Beam": {"damage": [20, 50], "level": 1},
            "Solar Flare X10": {"damage": [50, 65], "level": 20},
            "Neo Tri-Beam": {"damage": [65, 80], "level": 60},
            "Four-Arms Strike": {"damage": [80, 110], "level": 100}
        }
    }, 
    "Mega-SukunaX10white": {
        "hp": "500",
        "photo": "https://files.catbox.moe/kn4yq2.jpg", 
        "caption": "Sukuna is a villian from jjk{jujutsu kaise}which can manuplate Or hypnotyse people copy there abilities or can enter in there body.", 
        "base_stats": {"hp": 250, "atk": 178, "def": 237, "spe": 267,"acc": 91}, 
        "moves": {
            "Flame-Bomb": {"damage": [50, 70], "level": 1},
            "Hyper-beam": {"damage": [80, 140], "level": 40},
            "Soul destroy": {"damage": [150, 170], "level":80},
            "Domain-Expansion": {"damege": [200, 300], "level":100}
        }
    }
}
            

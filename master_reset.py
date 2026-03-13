from app import app, db, User, Post
from werkzeug.security import generate_password_hash

# 1. Define the Missing Team
team_data = [
    {"u": "Rohit", "bio": "Lead Systems Architect.", "d": "Rohit#0001", "i": "@rohit_dev", "lvl": 99},
    {"u": "Harvar", "bio": "Visual Architect.", "d": "Harvar#0001", "i": "@harvar_art", "lvl": 50},
    {"u": "Dinesh", "bio": "UI/UX Magician.", "d": "Dinesh#4040", "i": "@dinesh_ui", "lvl": 45},
    {"u": "Bhargav", "bio": "AI Logic Master.", "d": "Bhargav#AI", "i": "@bhargav_code", "lvl": 40},
    {"u": "Bora", "bio": "Weapon Artist.", "d": "Bora#FPS", "i": "@bora_guns", "lvl": 35},
    {"u": "Tarun", "bio": "Environment Artist.", "d": "Tarun#Map", "i": "@tarun_env", "lvl": 20},
    {"u": "Vinay", "bio": "Networking Engineer.", "d": "Vinay#Net", "i": "@vinay_mp", "lvl": 15},
    {"u": "Charan", "bio": "Gameplay Programmer.", "d": "Charan#Run", "i": "@charan_dev", "lvl": 10},
]

# 2. Define the Missing Assets
assets = [
    {"u": "Rohit", "t": "ULTIMATE HORROR SYSTEM", "f": "DOOR 1.mp4", "p": 1500, "d": "Full jumpscare logic."},
    {"u": "Harvar", "t": "ADVANCED CAR PHYSICS", "f": "car.mp4", "p": 2500, "d": "Drifting and suspension."},
    {"u": "Dinesh", "t": "RPG INVENTORY UI", "f": "human.mp4", "p": 899, "d": "Drag and drop inventory."},
    {"u": "Bhargav", "t": "DRONE AI SWARM", "f": "drone.mp4", "p": 1200, "d": "Autonomous pathfinding."},
    {"u": "Bora", "t": "FPS WEAPON PACK", "f": "tuuent.mp4", "p": 3000, "d": "10 High-fidelity weapons."},
    {"u": "Tarun", "t": "OPEN WORLD MAP", "f": "damge taker cube.mp4", "p": 4500, "d": "8x8km Landscape."},
    {"u": "Vinay", "t": "MULTIPLAYER CHAT", "f": "up jumping portal.mp4", "p": 600, "d": "Global voice chat."},
    {"u": "Charan", "t": "PARKOUR SYSTEM V2", "f": "human.mp4", "p": 1800, "d": "Climbing and vaulting."}
]

with app.app_context():
    print("🔧 STARTING MASTER RESET...")

    # --- PHASE 1: RESTORE USERS ---
    print("\n👤 Checking Users...")
    for member in team_data:
        user = User.query.filter_by(username=member['u']).first()
        if not user:
            new_user = User(
                username=member['u'], 
                email=f"{member['u'].lower()}@arizen.com", 
                password=generate_password_hash("123", method='pbkdf2:sha256'),
                is_premium=True,
                level=member['lvl'],
                bio=member['bio'],
                discord_id=member['d'],
                insta_id=member['i']
            )
            db.session.add(new_user)
            print(f"   [+] Created User: {member['u']}")
        else:
            print(f"   [OK] Found User: {member['u']}")
    
    db.session.commit() # Save users so we can link videos to them

    # --- PHASE 2: RESTORE VIDEOS ---
    print("\n🎬 Checking Assets...")
    for a in assets:
        post = Post.query.filter_by(title=a['t']).first()
        if not post:
            creator = User.query.filter_by(username=a['u']).first()
            if creator:
                new_post = Post(title=a['t'], filename=a['f'], price=a['p'], desc=a['d'], author=creator, sold_count=a['p']//10)
                db.session.add(new_post)
                print(f"   [+] Restored Video: {a['t']}")
            else:
                print(f"   [ERROR] Could not find creator for {a['t']}")
        else:
            print(f"   [OK] Found Video: {a['t']}")

    db.session.commit()
    print("\n✅ MASTER RESET COMPLETE. RESTART YOUR SERVER.")
from google import genai
from dotenv import load_dotenv
import os
import json
import datetime

#Load API key

load_dotenv()
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# CREATE REQUIRED FOLDERS

os.makedirs("profiles", exist_ok=True)
os.makedirs("history", exist_ok=True)

#Json functions

def load_json(filename,default):
    try:
        with open(filename,"r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return default
    
def save_json(filename,data):
    with open(filename,"w", encoding="utf-8") as file:
        return json.dump(data,file,indent=4)


#Create Profile

def create_profile():
    print("\nCreate Your AI Learning Profile\n")
    name=input("Your Name: ")

    #Check if profile already exists
    if os.path.exists(f"profiles/{name}.json"):
        print("\nProfile already exists!")
        return load_json(f"profiles/{name}.json", {})
    
    learning=input("What are your learning?: ")
    level=input("Your Level (Beginner/Intermediate/Advanced): ")
    goal=input("Your goal: ")

    profile={
        "name": name,
        "learning": learning,
        "level": level,
        "goal": goal
    }

    save_json(f"profiles/{name}.json", profile)
    print("\nProfile Created Successfully!")
    return profile

def update_profile(profile):

    print("\n===== UPDATE PROFILE =====\n")
    print(f"Current Learning Topic : {profile['learning']}")
    new_learning = input("New Learning Topic (press Enter to keep current): ")
    print(f"Current Level : {profile['level']}")
    new_level = input("New Level (press Enter to keep current): ")
    print(f"Current Goal : {profile['goal']}")
    new_goal = input("New Goal (press Enter to keep current): ")

    if new_learning.strip():
        profile['learning'] = new_learning
    if new_level.strip():
        profile['level'] = new_level
    if new_goal.strip():
        profile['goal'] = new_goal

    save_json(f"profiles/{profile['name']}.json", profile)
    print("\nProfile Updated Successfully!")
    return profile

# SELECT PROFILE

def select_profile():

    files = [
        file for file in os.listdir("profiles")
        if file.endswith(".json")
    ]

    if not files:
        print("\nNo profiles found!")
        return create_profile()

    print("\n===== AVAILABLE PROFILES =====\n")

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file[:-5]}")

    try:
        choice = int(input("\nSelect Profile Number: "))

        filename = files[choice - 1]

        return load_json(
            f"profiles/{filename}",
            {}
        )

    except:
        print("\nInvalid Choice!")
        return select_profile()

# View Profile

def view_profile(profile):
    print("\n===== CURRENT PROFILE =====\n")
    print(json.dumps(profile, indent=4))

#Ask Gemini

def ask_ai(question,profile):
    prompt=f"""

User Profile:

Name: {profile['name']}
Learning: {profile['learning']}
Level: {profile['level']}
Goal: {profile['goal']}

Answer according to the user's level.

Question: {question}
"""
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

#Save history

def save_history(user,bot,profile):
    filename = f"history/{profile['name']}_history.json"
    history=load_json(filename,[])

    history.append({
        "time": str(datetime.datetime.now()),
        "user": user,
        "bot": bot
    })
    save_json(filename, history)

     
#Show history

def show_history(profile):

    filename = f"history/{profile['name']}_history.json"
    history=load_json(filename,[])
    print(f"\nLoading history from: {filename}")
    if len(history) == 0:
        print("\nNo history found.")
        return
    
    print("\n===== CHAT HISTORY =====\n")

    for chat in history:
        print(f"Time : {chat['time']}")
        print(f"You : {chat['user']}")
        print(f"AI : {chat['bot']}")
        print("-" *170)

#Main program

profile = select_profile()
print(f"\nWelcome {profile['name']}!")

print("""
===================================
      PERSONAL AI MENTOR
===================================
      
Commands:
history       -> View History
profile       -> View Profile
updateprofile -> Update Profile
newprofile    -> Create New Profile
switch        -> Switch Profile
exit          -> Exit Program
===================================
""")

while True:
    user=input("\nYou: ")

    if user.lower()=="exit":
        print("AI: Goodbye!")
        break
    elif user.lower()=="history":
        show_history(profile)
    elif user.lower()=="profile":
          view_profile(profile)
    elif user.lower() == "updateprofile":
          profile = update_profile(profile)
    elif user.lower() == "newprofile":
          profile = create_profile()
          print(f"\nCurrent Profile: {profile['name']}")

    elif user.lower() == "switch":
        profile = select_profile()
        print(f"\nSwitched to {profile['name']}")
    else:
        try:
            answer=ask_ai(user,profile)
            print("\nAI:", answer)
            save_history(user,answer,profile)

        except Exception as e:
            print("Error:",e)




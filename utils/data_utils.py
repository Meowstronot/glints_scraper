from dotenv import load_dotenv, dotenv_values
import os

def glints_credential():

    env_data = dotenv_values("privacy/.env")
    if not env_data.get("GLINTS_EMAIL") or not env_data.get("GLINTS_PASSWORD"):
        
        email = input("Masukkan email glints: ")
        password = input("Masukkan password glints: ")
        with open("privacy/.env", "w") as f:
            f.write(f"GLINTS_EMAIL={email}\n")
            f.write(f"GLINTS_PASSWORD={password}\n")
    else:
        email = env_data.get("GLINTS_EMAIL")
        password = env_data.get("GLINTS_PASSWORD")    
        print(f"Email : {email}")
        print(f"Password: {password[1]+'*' * (len(password)-1)}")
        print("Email dan password sudah ada di 'privacy/.env'")


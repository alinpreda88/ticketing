import tkinter as tk
import os
import requests
import json
import socket
import hashlib
from datetime import datetime
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk  # PIL pentru imaginea de fundal

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def generare_token():
    # Obținem ziua curentă
    ziua_curenta = datetime.now().day
    
    # Obținem IP-ul și îl curățăm de puncte și ":"
    ip = get_ip()
    ip_curat = ip.replace(".", "").replace(":", "")
    
    # Cheia API
    api_key = "9137935D7F29133279AA06B574387F2F"
    
    # Pentru compatibilitate cu PHP, folosim encoding utf-8
    for i in range(ziua_curenta):
        # Data în format Ymd
        data = datetime.now().strftime("%Y%m%d")
        
        # Creăm hash-urile MD5 pentru fiecare component
        hash_data = hashlib.md5(data.encode('utf-8')).hexdigest()
        hash_ip = hashlib.md5(ip_curat.encode('utf-8')).hexdigest()
        hash_key = hashlib.md5(api_key.encode('utf-8')).hexdigest()
        
        # Combinăm hash-urile și creăm hash-ul final
        token = hashlib.md5((hash_data + hash_ip + hash_key).encode('utf-8')).hexdigest()
    
    return token

def on_submit():
    text = entry.get("1.0", tk.END).strip()
    selected_subject = subject_var.get()
    print(f"Text introdus: {text}")
    print(f"Subiect selectat: {selected_subject}")
    entry.delete("1.0", tk.END)
    
    url = "http://ticket.cmteb.ro/osTicket/api/http.php/tickets.json"
    
    payload = json.dumps({
        "name": user_name,
        "email": user_name + "@cmteb.ro",
        "staffId": 8,
        "topicId": 21,
        "subject": selected_subject,
        "message": text,
        "companyid": computer_name,
        "ip": ip,
        "attachments": ""
    })
    
    headers = {
        'x-api-key': '9137935D7F29133279AA06B574387F2F',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    print(response.text)
    
    entry.pack_forget()
    submit_button.pack_forget()
    subject_dropdown.pack_forget()
    
    try:
        ticket_number = int(response.text.strip())
    except ValueError:
        ticket_number = "Eroare la parsarea răspunsului"
    
    global ticket_label, new_ticket_button
    ticket_label = tk.Label(root, text=f"Ticketul d-voastra a fost preluat si are numarul: {ticket_number}", font=("Arial", 16), bg="#f0f0f0", fg="black")
    ticket_label.pack(pady=20)

    new_ticket_button = tk.Button(root, text="Ticket nou", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", relief="raised", borderwidth=3, command=reset_ui)
    new_ticket_button.pack(pady=10)

def refresh_tickets():
    global ticket_list_text, new_ticket_button
    
    entry.pack_forget()
    submit_button.pack_forget()
    subject_dropdown.pack_forget()
    if 'ticket_label' in globals():
        ticket_label.pack_forget()
    if 'user_info_label' in globals():
        user_info_label.pack_forget()

    # Reînnoim datele utilizatorului
    user_data = initialize_user_data()
    
    if 'ticket_list_text' not in globals():
        ticket_list_text = scrolledtext.ScrolledText(root, font=("Arial", 13), width=80, height=20, state="disabled", bg="white", fg="black")
    
    ticket_list_text.pack(pady=20)
    ticket_list_text.config(state="normal")
    ticket_list_text.delete("1.0", tk.END)
    
    # Mai întâi afișăm datele utilizatorului
    if user_data:
        ticket_list_text.insert(tk.END, "=== DATE UTILIZATOR ===\n")
        formatted_data = json.dumps(user_data, indent=2, ensure_ascii=False)
        ticket_list_text.insert(tk.END, formatted_data + "\n\n")
    
    # Apoi afișăm lista de tickete
    ticket_list_text.insert(tk.END, "=== LISTA TICKETE ===\n")
    url = f"http://ticket.cmteb.ro/osTicket/api/http.php/tickets.json?email={user_name}@cmteb.ro"
    headers = {'x-api-key': '9137935D7F29133279AA06B574387F2F'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets:
            ticket_list_text.insert(tk.END, f"Ticket #{ticket['id']}: {ticket['subject']}\n")
    else:
        ticket_list_text.insert(tk.END, "Eroare la preluarea ticketelor!\n")
    
    ticket_list_text.config(state="disabled")

    new_ticket_button = tk.Button(root, text="TICKET NOU", font=("Arial", 13, "bold"), 
                                 bg="#4CAF50", fg="white", relief="raised", borderwidth=3, 
                                 command=reset_ui)
    new_ticket_button.pack(pady=10)

def reset_ui():
    if 'ticket_list_text' in globals():
        ticket_list_text.pack_forget()
    if 'ticket_label' in globals():
        ticket_label.pack_forget()
    new_ticket_button.pack_forget()

    # Resetăm valorile și starea componentelor
    subject_var.set("Alege subiect")
    entry.delete("1.0", tk.END)
    submit_button.config(state="disabled")
    
    subject_label.pack()
    subject_dropdown.pack(pady=10)
    entry.pack(pady=20)
    submit_button.pack()

def check_fields(*args):
    # Verificăm dacă este selectat un subiect valid
    if subject_var.get() == "Alege subiect":
        submit_button.config(state="disabled")
        subject_label.config(text="Te rog alege un subiect!", fg="red")
        return
    else:
        subject_label.config(text="", fg="black")
    
    # Verificăm dacă există text în câmpul de mesaj
    text_content = entry.get("1.0", tk.END).strip()
    
    # Activăm butonul doar dacă ambele câmpuri sunt completate
    if text_content and subject_var.get() != "Alege subiect":
        submit_button.config(state="normal")
    else:
        submit_button.config(state="disabled")

def set_background(event=None):
    global bg_image, bg_label
    
    # Verificăm dacă fereastra există și are dimensiuni valide
    if not hasattr(root, 'winfo_width') or root.winfo_width() <= 1:
        return
        
    # Redimensionăm imaginea doar dacă dimensiunile s-au schimbat semnificativ
    new_width = root.winfo_width()
    new_height = root.winfo_height()
    
    if hasattr(set_background, 'last_size'):
        if abs(set_background.last_size[0] - new_width) < 50 and \
           abs(set_background.last_size[1] - new_height) < 50:
            return
            
    set_background.last_size = (new_width, new_height)
    
    # Redimensionăm imaginea pentru a se potrivi cu fereastra
    try:
        if not hasattr(set_background, 'original_img'):
            set_background.original_img = Image.open("background.jpg")
            
        img = set_background.original_img.copy()
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Creăm un layer alb pentru opacitate
        overlay = Image.new('RGBA', (new_width, new_height), 'white')
        
        # Convertim imaginea originală la RGBA dacă nu este deja
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Blend între imagine și overlay (0.7 reprezintă 70% opacitate)
        img = Image.blend(overlay.convert('RGB'), img.convert('RGB'), 0.6)
        
        bg_image = ImageTk.PhotoImage(img)
        
        # Actualizăm imaginea de fundal
        bg_label.config(image=bg_image)
        bg_label.image = bg_image
    except Exception as e:
        print(f"Eroare la încărcarea imaginii: {e}")

def initialize_user_data():
    try:
        url = "http://ticket.cmteb.ro/osTicket/api_cmteb/api_cmteb.php"
        
        payload = json.dumps({
            "name": user_name,
            "email": f"{user_name}@cmteb.ro"
        })
        
        headers = {
            'x-api-key': generare_token(),
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Eroare la inițializarea datelor: {e}")
        return None

# Obține informațiile despre sistem
user_name = os.getenv("USERNAME") or os.getenv("USER")
computer_name = os.getenv("COMPUTERNAME") or os.uname().nodename
ip = os.getenv("IP") or get_ip()

# Inițializăm datele utilizatorului
user_data = initialize_user_data()

# Crearea ferestrei principale
root = tk.Tk()
root.title("GENERARE TICKET")
#root.geometry("900x700")
root.state('zoomed')  # Adăugăm această linie pentru maximizare
root.iconbitmap("favicon.ico")  

# Setează imaginea de fundal inițială
try:
    img = Image.open("background.jpg")
    img = img.resize((900, 700), Image.Resampling.LANCZOS)
    
    # Adăugăm opacitate la imaginea inițială
    overlay = Image.new('RGBA', (900, 700), 'white')
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    img = Image.blend(overlay.convert('RGB'), img.convert('RGB'), 0.6)
    
    bg_image = ImageTk.PhotoImage(img)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

    # Reducem frecvența evenimentelor de redimensionare
    root.bind("<Configure>", lambda e: root.after(100, set_background))
except Exception as e:
    print(f"Eroare la încărcarea imaginii inițiale: {e}")
    # Creăm un fundal simplu în caz că imaginea nu poate fi încărcată
    bg_label = tk.Label(root, bg="lightgray")
    bg_label.place(relwidth=1, relheight=1)

# Creare header
header_frame = tk.Frame(root, bg="lightgray", height=50)
header_frame.pack(fill="x", padx=10, pady=10)

header_label = tk.Label(
    header_frame,
    text=f"Utilizator: {user_name}  |  Calculator: {computer_name}  |  IP: {ip}",
    font=("Arial", 14),
    bg="lightgray",
    anchor="w"
)
header_label.pack(side="left", padx=5)

header_button = tk.Button(header_frame, text="VEZI TICKETELE", font=("Arial", 13, "bold"), bg="#FF9800", fg="white", relief="raised", borderwidth=3, command=refresh_tickets)
header_button.pack(side="right", padx=10, pady=10)

# Label pentru mesajul de eroare al dropdown-ului
subject_label = tk.Label(root, text="", font=("Arial", 10), fg="red")
subject_label.pack()

# Crearea variabilei pentru dropdown
subject_var = tk.StringVar(value="Alege subiect")

# Dropdown pentru subiecte
subject_dropdown = ttk.Combobox(root, textvariable=subject_var, font=("Arial", 13), state="readonly")
subject_dropdown['values'] = ("Alege subiect", "Problema Hardware", "Problema Software", "Alte probleme")
subject_dropdown.pack(pady=60)

# Câmp text pentru mesaj
entry = scrolledtext.ScrolledText(root, width=90, height=20, font=("Arial", 13))
entry.pack(pady=20)

# Buton submit (inițial dezactivat)
submit_button = tk.Button(root, text="TRIMITE TICKET", font=("Arial", 13, "bold"), 
                         bg="#4CAF50", fg="white", relief="raised", borderwidth=3,
                         command=on_submit, state="disabled")
submit_button.pack()

# Adăugăm trace pentru variabila dropdown și binding pentru text
subject_var.trace('w', check_fields)
entry.bind('<KeyRelease>', lambda e: check_fields())

# Rularea ferestrei
root.mainloop()
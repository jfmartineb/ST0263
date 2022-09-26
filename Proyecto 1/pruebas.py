from requests import get

try: 
    response = get("http://localhost:50000")
    print("MElo")
    
except: 
    print("Mierda")

import os, yaml, subprocess, time, nest_asyncio, re, random, string
from pathlib import Path
from flask import current_app
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from argon2 import PasswordHasher, exceptions
from src.virtualization.digital_replica.schema_registry import SchemaRegistry

"""
    COMMON UTILITIES
"""
def raise_error(error, position, name, inputs):
    destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
    try:
        print(f"Error: {error}\n\t- at {position}\n\t- function: {name}")
        if not isinstance(inputs, list):
            inputs = [inputs]
        print("\t- inputs:")
        for i in inputs:
            print(f"\t\t- {i}")
        return
    except Exception as e:
        print(f"Error: {e} from raise_error function")
        return

def getenv_array(var_name):
    try:
        return os.getenv(var_name).split(',') if os.getenv(var_name) else []
    except Exception as e:
        raise_error(e, __file__, var_name)
        return []

def getenv_dict(var_name):
    try:
        env_var = getenv_array(var_name)
        return {item.split(':')[0]: item.split(':')[1] for item in env_var} if env_var else {}
    except Exception as e:
        raise_error(e, __file__, getenv_dict.__name__, var_name)
        return {}

def check_input_format(text, pattern):
    """
    Return True if `text` fully matches the regex `pattern`.
    
    `pattern` may be either a regex string or a compiled re.Pattern.
    """
    try:
        # Compile if user passed a pattern string
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        # fullmatch returns a Match object if the whole string matches
        return pattern.fullmatch(text) is not None
    except Exception as e:
        raise_error(e, __file__, check_input_format.__name__, [text, pattern])
        return False
    
def str_based_on_type(key, value):
    try:
        string = ''
        if type(value) == str:
            string=f'{key}: {value}\n'
        elif type(value) == dict:
            for k in value:                        
                string+=f'\t- {k}: {value[k]}\n'
        return string
    except Exception as e:
        raise_error(e, __file__, str_based_on_type.__name__, [key, value])
        return ''

def print_response(response):
    try:
        if not response.json():
            return os.getenv("ERROR_MESSAGE")
        if not response.json().get("status"):
            return os.getenv("Request not successful")
        if response.json().get("status") == "error":
            return response.json().get("message", os.getenv("ERROR_MESSAGE"))
        if response.json().get("status") == "success":
            text = ''
            if response.json().get("message"):
                text+=f'{response.json().get("message")}\n'
            for key in response.json():
                if not key == 'status' and not key == 'message':
                    if not type(response.json()[key]) == list:
                        text+=str_based_on_type(key, response.json()[key])
                    else:
                        text+=f'{key}:\n'
                        for item in response.json()[key]:
                            text+=f'\t{str_based_on_type("", item)}'
                            text+='-'*64+'\n'
            return text
    except Exception as e:
        raise_error(e, __file__, print_response.__name__, [response])
        return os.getenv("ERROR_MESSAGE")
    
def check_api_source(data):
    try:
        if not check_temp_token(data["temp_token"]):
            destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
            return None
        else:
            return "Telegram"
    except Exception as e:
        raise_error(e, __file__, check_api_source.__name__, '')
        return None
    
def get_month_strings():
    return {
        "full": [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ],
        "abbr": [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"
        ]
    }

def handle_month(month):
    try:
        if isinstance(month, str):
            month = month.strip()
            months_full = get_month_strings()["full"]
            months_abbr = get_month_strings()["abbr"]
            month_lower = month.lower()
            if month_lower in months_full:
                return months_full.index(month_lower) + 1
            elif month_lower in months_abbr:
                return months_abbr.index(month_lower) + 1
            elif month.isdigit():
                month_int = int(month)
                if 1 <= month_int <= 12:
                    return month_int
                else:
                    return None
            else:
                return None
        elif isinstance(month, int):
            if 1 <= month <= 12:
                return month
            else:
                return None
        else:
            return None
    except Exception as e:
        raise_error(e, __file__, handle_month.__name__, [month])
        return None

def handle_year(year):
    try:
        if isinstance(year, str):
            year = year.strip()
            if year.isdigit():
                year_int = int(year)
                current_year = datetime.now().year
                if len(year) == 4:
                    if 2000 <= year_int <= current_year:
                        return year_int
                    else:
                        return None
                elif len(year) == 2:
                    if 0 <= year_int <= (current_year - 2000):
                        return 2000 + year_int
                    else:
                        return None
                else:
                    return None
            else:
                return None
        elif isinstance(year, int):
            current_year = datetime.now().year
            if 2000 <= year <= current_year:
                return year
            elif 0 <= year <= (current_year - 2000):
                return 2000 + year
            else:
                return None
        else:
            return None
    except Exception as e:
        raise_error(e, __file__, handle_year.__name__, [year])
        return None

def handleDMY(DMYstring):
    """
        The time string must be: DD_MM_YY
    """
    try:
        return {
            "day": int(DMYstring.split("_")[0]),
            "month": int(DMYstring.split("_")[1]),
            "year": int(2000 + int(DMYstring.split("_")[2]))
        }
    except Exception as e:
        raise_error(e, __file__, handleDMY.__name__, [DMYstring])
        return None

def handle_hour(hour):
    try:
        if isinstance(hour, str):
            hour = hour.strip().lower()      
            if "m" in hour:
                hour = hour.replace("m", "").lower()
            if "." in hour:
                hour = hour.replace(".", "").lower()
            if "a" in hour:
                hour = hour.replace("a", "").lower()
            if "p" in hour:
                hour = hour.replace("p", "").lower()
            if hour.isdigit():
                hour = int(hour)
                if 1 <= hour <= 12:
                    return hour + 12
                else:
                    return None
    except Exception as e:
        raise_error(e, __file__, handle_hour.__name__, [hour])
        return None

def handleHMS(HMSstring):
    """
        The time string must be: HH:MM:SS
    """ 
    try:
        return{
            "hour": int(HMSstring.split(":")[0]),
            "minute": int(HMSstring.split(":")[1]),
            "second": int(HMSstring.split(":")[2])
        }
    except Exception as e:
        raise_error(e, __file__, handleHMS.__name__, [HMSstring])
        return None
    
def handleUNC(UNCstring):
    """
        The time string must either be:
        - any/any/any -> Day/Month/Year
        - any:{2 digits}:{2 digits} -> Hour:Minute:Second
        - any/{4 digits} -> Month/Year
        - any/any -> Day/Month
        - any:{2 digits} -> Hour:Minute
        - {4 digits} -> Year
        - {month string} -> Month
        - {2 digits} | {string containing a dot} | {string containing am or pm} -> Hour
    """
    try:
        if "/" in UNCstring or (UNCstring.isdigit() and len(UNCstring) == 4) or \
            UNCstring.strip().lower() in get_month_strings()["full"] or \
            UNCstring.strip().lower() in get_month_strings()["abbr"]:
            # Handle DMY string
            dmy = handleDMY(UNCstring)
            return {
                "day": int(dmy["day"]),
                "month": int(dmy["month"]),
                "year": int(dmy["year"]),
                "hour": 0,
                "minute": 0,
                "second": 0
            }
        elif ":" in UNCstring or (UNCstring.isdigit() and len(UNCstring) == 2) or \
            "." in UNCstring or "am" in UNCstring.strip().lower() or "pm" in UNCstring.strip().lower():
            # Handle HMS string
            hms = handleHMS(UNCstring)
            return {
                "day": datetime.now().day,
                "month": datetime.now().month,
                "year": datetime.now().year,
                "hour": int(hms["hour"]),
                "minute": int(hms["minute"]),
                "second": int(hms["second"])
            }
        else:
            return None

    except Exception as e:
        raise_error(e, __file__, handleUNC.__name__, [UNCstring])
        return None

def string_to_datetime(date_string):
    """
        The time string must be DD_MM_YY-HH:MM:SS
    """
    try:
        dmy = handleDMY(date_string.split("-")[0])
        hms = handleHMS(date_string.split("-")[1])
        return datetime(
            year=int(dmy["year"]),
            month=int(dmy["month"]),
            day=int(dmy["day"]),
            hour=int(hms["hour"]),
            minute=int(hms["minute"]),
            second=int(hms["second"])
        )
    except Exception as e:
        raise_error(e, __file__, string_to_datetime.__name__, [date_string])
        return None

"""
    CONFIGURATION FUNCTIONS
"""

def create_db_data():
    try:
        db_schema = os.getenv("DB_SCHEMA")
        db_data = {
            'database': {
                'connection': {
                    'host': os.getenv("DB_HOST"),
                    'port': os.getenv("DB_PORT"),
                    'username': os.getenv("DB_USERNAME"),
                    'password': os.getenv("DB_PASSWORD")
                },
                'settings': {
                    'name': os.getenv("DB_NAME"),
                    'auth_source': os.getenv("DB_AUTH_SOURCE") 
                }
            }
            }
        with open(db_schema, 'w') as file:
            yaml.dump(db_data, file)
    except Exception as e:
        raise_error(e, __file__, create_db_data.__name__, [db_schema])
        return

def get_schemas_names():
    try:
        schemas_path = os.getenv("SCHEMAS_PATH")
        if not schemas_path:
            raise ValueError("SCHEMAS_PATH is not set in the environment variables.")
        try:
            return getenv_dict("SCHEMAS")
        except Exception as e:
            raise ValueError(f"Failed to load schema from {schemas_path}: {str(e)}")
    except Exception as e:
        raise_error(e, __file__, get_schemas_names.__name__, [schemas_path])
        return {}
    
def load_schemas():
    try:
        schema_registry = SchemaRegistry()
        schemas_path = os.getenv("SCHEMAS_PATH")            
        schemas = get_schemas_names()
        try:       
            for key, value in schemas.items():
                schema_registry.load_schema(key, schemas_path + value)
                print(f'Loaded {key} schema: {schemas_path + value}')
        except:
            print(f"Failed to load schemas from {schemas_path}")
    except Exception as e:
        raise_error(e, __file__, load_schemas.__name__, [schemas_path])
        return

def start_mosquitto():
    try:
        print('Killing existing Mosquitto process...', end='\n\n')
        proc = subprocess.Popen(
            'netstat -ano | findstr :1883',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        pids = []

        for line in iter(proc.stdout.readline, b''):
            line = line.decode().strip()
            pids.append(line.split()[-1])

        proc.stdout.close()

        proc.kill()

        for pid in pids:
            kill_command = f'taskkill /PID {pid}  /F'
            print(f'Killing process with PID: {pid}')
            os.system(kill_command)
            time.sleep(0.5)

        print("All existing Mosquitto processes have been killed.")

        time.sleep(2)

        os.system('cls' if os.name == 'nt' else 'clear')
        print('Starting Mosquitto...')

        mosquitto_command ='mosquitto -v -c "' + os.getcwd().replace('\\','/') +'/config/mosquitto.conf"'
        proc = subprocess.Popen(
            mosquitto_command, 
            creationflags=subprocess.CREATE_NO_WINDOW, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        for line in iter(proc.stdout.readline, b''):
            line = line.decode().strip()
            print(line)
            if line.__contains__('mosquitto version') and line.__contains__('running'):
                print('Mosquitto started successfully')
                break

        proc.stdout.close()

        time.sleep(2)

        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        raise_error(e, __file__, start_mosquitto.__name__, [mosquitto_command])
        return

def configure():
    try:
        # Patch asyncio to allow nested event loops (async/await inside sync code)
        nest_asyncio.apply()
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")
        print("Starting Mosquitto broker...")
        # Start Mosquitto broker
        start_mosquitto()
        print("Mosquitto broker started.\nCreating database data...")    
        # Create database data
        create_db_data()
    except Exception as e:
        raise_error(e, __file__, configure.__name__, [])
        return

"""
    DATABASE UTILITIES
"""

def query_db(collection, command):
    try:
        db_service = current_app.config["DB_SERVICE"]
        if not isinstance(collection, list):
            collection = [collection]
        if not isinstance(command, list):
            command = [command]
        findings = []
        for coll in collection:
            for cmd in command:
                try:
                    result = db_service.query_drs(coll, cmd)
                    if not isinstance(result, list):
                        findings.append(result)
                    else:
                        for res in result:
                            findings.append(res)
                except Exception as e:
                    pass
        return findings
    except Exception as e:
        raise_error(e, __file__, query_db.__name__, [collection, command])
        return []

def update_db(collection, query, updated_data):
    try:
        db_service = current_app.config["DB_SERVICE"]
        elements = query_db(collection, query)
        if not elements:
            print(f"Element not found in {collection} with query {query}")
            return
        if not isinstance(updated_data, list):
            updated_data = [updated_data]
        if not isinstance(elements, list):
            elements = [elements]
        for els in elements:
            if not isinstance(els, list):
                els = [els]
            for el in els:
                upd = nest_dot_keys(updated_data)
                metadata = el["metadata"]          
                if "metadata" in upd:
                    for key in metadata:
                        if key not in upd["metadata"]:
                            upd["metadata"][key] = metadata[key]
                db_service.update_dr(
                    collection,
                    el["_id"],
                    upd
                )
    except Exception as e:
        raise_error(e, __file__, update_db.__name__, [collection, query, updated_data])
        return
def save_element_in_db(collection, element):
    try:
        db_service = current_app.config["DB_SERVICE"]
        db_service.save_dr(collection, element)
    except Exception as e:
        raise_error(e, __file__, save_element_in_db.__name__, [collection, element])
        return
    
def delete_element_from_db(collection, element):
    try:
        db_service = current_app.config["DB_SERVICE"]
        db_service.delete_dr(collection, element["_id"])
    except Exception as e:
        raise_error(e, __file__, delete_element_from_db.__name__, [collection, element])
        return

def register_user(data, collection):
    try:
        """
            Check if there are any other users with the
                same username/reg_plate and uid
        """
        element = {
            "_id": "",
            "type": "",
            "data": {},
            "metadata": {},
            "profile": {}
        }
        response = {}
        if "username" in data:
            identifier = data["username"]
            element["profile"]["username"] = data["username"]
            response["username"] = data["username"]
        elif "reg_plate" in data:
            identifier = data["reg_plate"]
            element["profile"]["reg_plate"] = data["reg_plate"]
            response["reg_plate"] = data["reg_plate"]
        else:
            return None
        same_users = query_db(
            collection, 
            [
                {"profile.username": identifier},
                {"profile.reg_plate": identifier},
                {"profile.uid": data["uid"].replace("_", " ")}
            ]
        )
        if same_users:
            return {
                "status": "error",
                "message": "User with the same identifier or UID exists"
            }
        element["_id"] = generate_unique_id(collection)
        element["type"] = collection[:-1]
        element["metadata"] = {
            "logged_as": None,
            "updated_at": datetime.now(),
            "created_at": datetime.now()
        }
        element["data"] = {
            "exit": [],
            "enter": []
        }
        element["profile"]["password"] = hash_password(data["password"])
        element["profile"]["uid"] = data["uid"]
        element["profile"]["atHome"] = False
        response["_id"] = element["_id"]
        response["type"] = element["type"]
        response["uid"] = element["profile"]["uid"]

        save_element_in_db(collection, element)
        return {
            "status": "success",
            "message": f"Registered user",
            "data": response
        }
    except Exception as e:
        raise_error(e, __file__, register_user.__name__, [data, collection])
        return

def delete_user(data, identifier, collection):
    # Try to find the user
    try:
        users = query_db(
            collection, 
            [
                {"_id": identifier}, 
                {"profile.uid": identifier.replace("_", " ")},
                {"profile.username": identifier},
                {"profile.reg_plate": identifier}
            ]
        )
        if not users:
            return {
                "status": "error",
                "message": "User not found"
            }
        if len(users) > 1:
            return {
                "status": "error",
                "message": "Multiple users found with the same identifier"
            }
        user = users
        while isinstance(user, list):
            user = user[0]
        response = {
            "_id": user["_id"],
            "type": user["type"],
            "uid": user["profile"]["uid"]
        }
        if user["type"] == "pedestrian":
            logged_in_users.pop(user["_id"], None)
            response["username"] = user["profile"]["username"]
        elif user["type"] == "car":
            logged_in_users.pop(user["_id"], None)
            response["reg_plate"] = user["profile"]["reg_plate"]
        else:
            return {
                "status": "error",
                "message": "User type not recognized"
            }
        delete_element_from_db(collection, user)
        return {
            "status": "success",
            "message": "Deleted user",
            "data": response
        }
    except Exception as e:
        raise_error(e, __file__, delete_user.__name__, [data, identifier, collection])
        return
    
def show_users_list(users_found):
    try:
        users = []
        for user in users_found:
            users.append({
                    "_id": user["_id"],
                    "type": user["type"],
                    "uid": user["profile"]["uid"]
                })
            try:
                users["username"] = user["profile"]["username"]
            except:
                pass
            try:
                users["reg_plate"] = user["profile"]["reg_plate"]
            except:
                pass
        return users
    except Exception as e:
        raise_error(e, __file__, show_users_list.__name__, [users_found])
        return []

def find_users(data, collection):
    try:
        users_found = query_db(collection, [{}])
        return {
            "status": "success",
            "message": "Users found",
            "data": show_users_list(users_found)
        }
    except Exception as e:
        raise_error(e, __file__, find_users.__name__, [data, collection])
        return

def find_user(data, command, collection):
    try:
        users_found = query_db(
            collection, 
            [
                {"_id": command}, 
                {"profile.uid": command.replace("_", " ")},
                {"profile.username": command},
                {"profile.reg_plate": command.replace("_", " ")}
            ]
        )
        if len(users_found) <= 0:
            return {
                "status": "error",
                "message": "Something went wrong"
            }
        return {
            "status": "success",
            "message": "Users found",
            "data": show_users_list(users_found)
        }
    except Exception as e:
        raise_error(e, __file__, find_user.__name__, [data, command, collection])
        return

def get_open_array(identifier, open):
    try:
        collections = getenv_array("COLLECTIONS")
        if not collections:
            return {
            "status": "ERROR",
            "message": "COLLECTIONS is not set in the environment variables."
        }
        users = query_db(
            collections,
            [
                {"_id": identifier},
                {"profile.uid": identifier.replace("_", " ")},
                {"profile.username": identifier},
                {"profile.reg_plate": identifier.replace("_", " ")}
            ]
        )
        if not users:
            return {
                "status": "error",
                "message": "User not found"
            }
        if len(users) > 1:
            return {
                "status": "error",
                "message": "Multiple users found with the same identifier"
            }
        user = users
        while isinstance(user, list):
            user = user[0]
        return {
            "status": "success",
            "message": "Open array found",
            "data": user["data"][open]
        }
    except Exception as e:
        raise_error(e, __file__, get_open_array.__name__, [identifier, open])
        return

"""
    TELEGRAM UTILITIES
"""

# Dictionary to track logged-in users
logged_in_users = {}

def nest_dot_keys(pairs):
    try:
        out = {}
        for single in pairs:
            for flat_key, value in single.items():
                parts = flat_key.split(".")
                d = out
                # drill down, creating intermediate dicts as needed
                for p in parts[:-1]:
                    if p not in d or not isinstance(d[p], dict):
                        d[p] = {}
                    d = d[p]
                # set the final leaf
                d[parts[-1]] = value
        return out
    except Exception as e:
        raise_error(e, __file__, nest_dot_keys.__name__, [pairs])
        return {}
    
def create_temporary_token():
    try:
        random_token = ''
        random_token+=random.choice(string.ascii_lowercase)
        random_token+=random.choice(string.ascii_uppercase)
        random_token+=random.choice(string.digits)
        extra_symbols=['?', '!', '$', '%', '^', '&', '*']
        random_token+=random.choice(extra_symbols)
        all_chars = list(
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
        ) + extra_symbols
        for i in range(60):
            random_token+=random.choice(all_chars)
        chars = list(random_token)
        random.shuffle(chars)
        random_token = ''.join(chars)
        return random_token
    except Exception as e:
        raise_error(e, __file__, create_temporary_token.__name__, [])
        return None

def save_temporary_token_hash(path, token):
    try:
        ph=PasswordHasher()
        hashed_token = ph.hash(token)
        with open(path, 'w') as file:
            file.write(hashed_token)
        return
    except Exception as e:
        raise_error(e, __file__, save_temporary_token_hash.__name__, [path, token])
        return

def destroy_temporary_token(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        raise_error(e, __file__, destroy_temporary_token.__name__, [path])
        return

def check_temp_token(submitted_token):
    try:
        real_token = None
        with open(os.getenv("TEMP_TOKEN_PATH"), 'r') as file:
            real_token = file.read()
        if not real_token or not submitted_token:
            return False
        return verify_password(real_token, submitted_token)
    except Exception as e:
        raise_error(e, __file__, check_temp_token.__name__, [submitted_token])
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return False

def verify_password(real_password, inserted_password):
    try:
        ph = PasswordHasher()
        try:
            ph.verify(real_password, inserted_password)
            return True
        except exceptions.VerifyMismatchError:
            return False
    except Exception as e:
        raise_error(e, __file__, verify_password.__name__, [real_password, inserted_password])
        destroy_temporary_token(os.getenv("TEMP_TOKEN_PATH"))
        return False
    
def hash_password(password):
    try:
        ph = PasswordHasher()
        return ph.hash(password)
    except Exception as e:
        raise_error(e, __file__, hash_password.__name__, [password])
        return None

def is_admin(telegram_id):
    try:
        if telegram_id in logged_in_users and "username" in logged_in_users[telegram_id]:
            return logged_in_users[telegram_id]["username"] == os.getenv("ADMIN_USERNAME")
        return False
    except Exception as e:
        raise_error(e, __file__, is_admin.__name__, telegram_id)
        return False

def ask_for_admin_pwd(update, context, conversation):
    try:
        telegram_id = update.effective_user.id
        try:
            if is_admin(telegram_id):
                context.user_data["conversation"] = conversation
                context.user_data["input"] = update.message.text
                response = "Please, write the admin password"
                return response, update, context
            else:
                response = os.getenv("ERROR_MESSAGE")
                context.user_data["conversation"] = None
        except:
            response = os.getenv("ERROR_MESSAGE")
            context.user_data["conversation"] = None
        return response, update, context
    except Exception as e:
        raise_error(e, __file__, ask_for_admin_pwd.__name__, [update, context])
        response = os.getenv("ERROR_MESSAGE")
        context.user_data["conversation"] = None
        return response, update, context

def check_auth(telegram_id: int) -> bool:
    try:
        return telegram_id in logged_in_users
    except Exception as e:
        raise_error(e, __file__, check_auth.__name__, telegram_id)
        return False

def login_in_db(collection, element, login_status):
    try:
        update_db(
            collection,
            {"_id": element["_id"]},
            [{"metadata.logged_as": login_status}, {"metadata.updated_at": datetime.now()}]
        )
    except Exception as e:
        raise_error(e, __file__, login_in_db.__name__, [collection, element, login_status])
        return
    
def generate_unique_id(collection):
    """ 
        Generate a unique ID for the user:
        The ID is based on the number of documents in the collection, padded to 4 digits 
    """
    try:
        all_users = query_db(collection, {})
        existing_ids = []
        for doc in all_users:
            try:
                if re.fullmatch(r'[PC]\d{4}', doc["_id"]):
                    existing_ids.append(int(doc["_id"].replace("C", "").replace("P", "")))
            except ValueError:
                continue

        new_id = 0
        if existing_ids:
            for i in range(max(existing_ids) + 1):
                if i not in existing_ids:
                    new_id = i
                    break
            else:
                new_id = max(existing_ids) + 1

        # Check if the ID is less than 9999
        if int(new_id) >= 9999:
            return None

        # Pad the ID to 4 digits
        if collection == 'pedestrians':
            return f"P{new_id:04}"
        elif collection == 'cars':
            return f"C{new_id:04}"
    except Exception as e:
        raise_error(e, __file__, login_in_db.__name__, [collection])

def update_logged_in_users(telegram_id, user):
    try:
        already_logged_in = False
        if telegram_id in logged_in_users:
            if logged_in_users[telegram_id]["_id"] == user["_id"]:
                """
                    Storing the already_logged_in flag, but continuing the operations
                        nonetheless, to avoid discrepancies between the DB and the
                        logged_in_users dictionary.
                """
                already_logged_in = True
            previously_logged_user = query_db(
                ["pedestrians", "cars"],
                {"_id": logged_in_users[telegram_id]["_id"]}
            )[0]
            del logged_in_users[telegram_id]
            login_in_db(previously_logged_user["type"]+"s", previously_logged_user, None)    
        logged_in_users[telegram_id] = {
            "_id": user["_id"],
            "uid": user["profile"]["uid"]
            }
        if user["type"] == "pedestrian":
            logged_in_users[telegram_id]["username"] = user["profile"]["username"]
        elif user["type"] == "car":
            logged_in_users[telegram_id]["reg_plate"] = user["profile"]["reg_plate"]
        login_in_db(user["type"]+"s", user, telegram_id)
        return {
            "success": True,
            "already_logged_in": already_logged_in
        }
    except Exception as e:
        raise_error(e, __file__, update_logged_in_users.__name__, [telegram_id, user])
        return {
            "success": False,
            "already_logged_in": False
        }

def remove_from_logged_in(telegram_id, user):
    try:
        login_in_db(user["type"]+"s", user, None)
        del logged_in_users[telegram_id]
    except Exception as e:
        raise_error(e, __file__, remove_from_logged_in.__name__, [telegram_id, user])
        return
    
def get_user_data(telegram_id: int) -> dict:
    try:
        return logged_in_users.get(telegram_id)
    except Exception as e:
        raise_error(e, __file__, get_user_data.__name__, telegram_id)
        return {}
    
def clear_logged_in_users():
    try:
        logged_in_users = {}
    except Exception as e:
        raise_error(e, __file__, clear_logged_in_users.__name__, [])

def handle_time_input(time_input):
    try:
        if not string_to_datetime(time_input):
            return """
Time input must be DD_MM_YY-HH:MM:SS
    E.g: 12_05_23-14:30:00
"""
        else:
            return True
    except Exception as e:
        raise_error(e, __file__, handle_time_input.__name__, [time_input])
        return os.getenv("ERROR_MESSAGE")
    
def start_time_is_before_end_time(start_time, end_time):
    if string_to_datetime(start_time) > string_to_datetime(end_time):
        return False
    return True

def get_num_of_open_times(data, identifier):
    try:
        start_time = string_to_datetime(data["start_time"])
        end_time = string_to_datetime(data["end_time"])
        open_array = get_open_array(identifier, data["open"])["data"]
        count = 0
        for open_time in open_array:
            if start_time <= open_time <= end_time:
                count += 1
        return {
            "status": "success",
            "message": f"The user has {data['open']}ed the door {count} times between {start_time} and {end_time}",
            "count": count,
        }
    except Exception as e:
        raise_error(e, __file__, get_num_of_open_times.__name__, [data, identifier])
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

def get_anonymous_open_times(data, collection = getenv_array("COLLECTIONS")):
    try:
        all_users = query_db(collection, [{}])
        all_ids = []
        for user in all_users:
            try:
                if re.fullmatch(r'[PC]\d{4}', user["_id"]):
                    all_ids.append(user["_id"])
            except ValueError:
                continue
        count = 0
        for id in all_ids:
            count += get_num_of_open_times(data, id)["count"]
            print(f"Processed user {id} for get_anonymous_open_times, count: {count}")
        print(f"The count for get_anonymous_open_times is {count}")
        return {
            "status": "success",
            "message": f"Users have {data['open']}ed the door {count} times between {data['start_time']} and {data['end_time']}",
            "count": count,
        }
    except Exception as e:
        raise_error(e, __file__, get_anonymous_open_times.__name__, [data, collection])
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

def get_open_times_stats_yearly(start_time, end_time, enter_array, exit_array):
    try:
        start_time = start_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = end_time.replace(year=end_time.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        current_time = start_time
        data = {}
        while current_time < end_time:
            next_time = current_time + relativedelta(years=1)
            data[current_time.year] = {
                "enter": 0,
                "exit": 0
            }
            for en in enter_array:
                if current_time <= en <= next_time:
                    data[current_time.year]["enter"] += 1
            for ex in exit_array:
                if current_time <= ex <= next_time:
                    data[current_time.year]["exit"] += 1
            current_time = next_time
        return data
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats_yearly.__name__, [start_time, end_time, enter_array, exit_array])
        return None

def get_open_times_stats_monthly(start_time, end_time, enter_array, exit_array):
    try:
        current_time = start_time
        data = {}
        while current_time < end_time:
            key = str(current_time)
            next_time = current_time + relativedelta(months=1)
            data[key] = {
                "enter": 0,
                "exit": 0
            }
            for en in enter_array:
                if current_time <= en <= next_time:
                    data[key]["enter"] += 1
            for ex in exit_array:
                if current_time <= ex <= next_time:
                    data[key]["exit"] += 1
            current_time = next_time
        return data
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats_monthly.__name__, [start_time, end_time, enter_array, exit_array])
        return None
    
def get_open_times_stats_daily(start_time, end_time, enter_array, exit_array):
    try:
        current_time = start_time
        data = {}
        while current_time < end_time:
            key = str(current_time)
            next_time = current_time + timedelta(days=1)
            data[key] = {
                "enter": 0,
                "exit": 0
            }
            for en in enter_array:
                if current_time <= en <= next_time:
                    data[key]["enter"] += 1
            for ex in exit_array:
                if current_time <= ex <= next_time:
                    data[key]["exit"] += 1
            current_time = next_time
        return data
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats_daily.__name__, [start_time, end_time, enter_array, exit_array])
        return None

def get_open_times_stats_hourly(start_time, end_time, enter_array, exit_array):
    try:
        current_time = start_time
        data = {}
        while current_time < end_time:
            key = str(current_time)
            next_time = current_time + timedelta(hours=1)
            data[key] = {
                "enter": 0,
                "exit": 0
            }
            for en in enter_array:
                if current_time <= en <= next_time:
                    data[key]["enter"] += 1
            for ex in exit_array:
                if current_time <= ex <= next_time:
                    data[key]["exit"] += 1
            current_time = next_time
        return data
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats_hourly.__name__, [start_time, end_time, enter_array, exit_array])
        return None

def get_time_interval_duration(start_time, end_time):
    try:
        # Convert start_time and end_time to datetime if they are not already
        if not isinstance(start_time, datetime):
            start_time = string_to_datetime(start_time)
        if not isinstance(end_time, datetime):
            end_time = string_to_datetime(end_time)
        if not start_time or not end_time:
            return {
            "status": "error",
            "message": "Invalid start_time or end_time."
            }
        duration = (end_time - start_time).total_seconds() / 3600  # duration in hours
        return {
            "status": "success",
            "duration_hours": duration
        }
    except Exception as e:
        raise_error(e, __file__, get_time_interval_duration.__name__, [start_time, end_time])
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

def get_open_times_stats(data, collection = getenv_array("COLLECTIONS")):
    try:
        all_users = query_db(collection, [{}])
        all_ids = []
        for user in all_users:
            try:
                if re.fullmatch(r'[PC]\d{4}', user["_id"]):
                    all_ids.append(user["_id"])
            except ValueError:
                continue
        start_time = string_to_datetime(data["start_time"])
        end_time = string_to_datetime(data["end_time"])
        enter_array = []
        exit_array = []
        for open in ["enter", "exit"]:
            for id in all_ids:
                open_array = get_open_array(id, open)["data"]
                for open_time in open_array:
                    if start_time <= open_time <= end_time:
                        if open == "enter":
                            enter_array.append(open_time)
                        elif open == "exit":
                            exit_array.append(open_time)
        time_interval = get_time_interval_duration(start_time, end_time)
        if time_interval["status"] == "error" or time_interval["duration_hours"] <= 0:
            return {
                "status": "error",
                "message": time_interval["message"]
            }
        if time_interval["duration_hours"] < 1:
            # Just counts
            enter_count = len(enter_array)
            exit_count = len(exit_array)
            return {
                "status": "success",
                "message": f"Users entered {enter_count} times and exited {exit_count} times in the last hour.",
                "data": {
                    "enter": enter_count,
                    "exit": exit_count
                }
            }
        elif time_interval["duration_hours"] < 48:
            # Hourly statisticss
            return {
                "status": "success",
                "message": "Hourly statistics collected.",
                "data": get_open_times_stats_hourly(start_time, end_time, enter_array, exit_array)
            }
        elif time_interval["duration_hours"] < 1440:
            # Daily statistics
            return {
                "status": "success",
                "message": "Daily statistics collected.",
                "data": get_open_times_stats_daily(start_time, end_time, enter_array, exit_array)
            }
        elif time_interval["duration_hours"] < 17568:
            # Monthly statistics
            return {
                "status": "success",
                "message": "Monthly statistics collected.",
                "data": get_open_times_stats_monthly(start_time, end_time, enter_array, exit_array)
            }
        elif time_interval["duration_hours"] > 17568:
            # Yearly statistics
            return {
                "status": "success",
                "message": "Yearly statistics collected.",
                "data": get_open_times_stats_yearly(start_time, end_time, enter_array, exit_array)
            }
        return {
            "status": "error",
            "message": "Could not determine the time interval.",
        }
    except Exception as e:
        raise_error(e, __file__, get_open_times_stats.__name__, [data, collection])
        return {
            "status": "error",
            "message": "An error occurred while processing the request.",
        }

"""
    TESTING UTILITIES
"""

def test_telegram_connection():
    try:
        import requests
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/getMe"
        response = requests.get(url)
        if response.status_code == 200:
            print("Telegram connection is working.")
        else:
            print("Failed to connect to Telegram.")
    except Exception as e:
        print(f"Error connecting to Telegram: {str(e)}")
    return True

def test_mongo_connection():
    from pymongo import MongoClient
    try:
        client = MongoClient(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            authSource=os.getenv("DB_AUTH_SOURCE")
        )
        db = client[os.getenv("DB_NAME")]
        collections = db.list_collection_names()
        print("Existing collections:")
        for collection in collections:
            print(f"- {collection}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
    return True

def test_MQTT():
    import paho.mqtt.client as mqtt

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker successfully.")
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}")

    def on_publish(client, userdata, mid):
        print(f"Message published with mid: {mid}")

    try:
        mqtt_broker = os.getenv("MQTT_BROKER")
        mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        mqtt_topic = os.getenv("MQTT_TOPIC", "test/topic")
        mqtt_message = os.getenv("MQTT_MESSAGE", "Hello, MQTT!")

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_publish = on_publish

        client.connect(mqtt_broker, mqtt_port, 60)
        client.loop_start()

        result, mid = client.publish(mqtt_topic, mqtt_message)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message '{mqtt_message}' published to topic '{mqtt_topic}'.")
        else:
            print(f"Failed to publish message to topic '{mqtt_topic}'.")
        
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"Error testing MQTT: {str(e)}")

"""
def test_all():
    print(f'\n{"#"*32}\nTESTING ALL CONNECTIONS\n\nTELEGRAM')
    test_telegram_connection()
    print("\nMONGODB")
    test_mongo_connection()
    print("\nMQTT")
    test_MQTT()
    print(f'\nALL CONNECTIONS TESTED\n{"#"*32}\n')
"""
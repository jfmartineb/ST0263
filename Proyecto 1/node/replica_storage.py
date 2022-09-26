import config
import pickle


data = {}


def set(key: str, value: str):
    global data
    data[key] = value
    save()


def get(key: str):
    print(f"Getting {key}")
    return data.get(key, None)


def delete(key: str):
    global data
    if key in data:
        del data[key]
        save()
        return True
    return False


def save():
    data_file = open(config.get_repl_path(id), 'wb')
    pickle.dump(data, data_file)
    data_file.close()


def load(idR):
    global id, data, data_file
    id = idR
    try:
        data_file = open(config.get_repl_path(id), 'rb')
        data = pickle.load(data_file)
        print(data)
        data_file.close()
    except FileNotFoundError:
        data = {}
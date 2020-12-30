from datetime import datetime
def name_change(name):
    file_tail = datetime.now().strftime("%m%d%Y%H%M%S%f")
    return name.strip()+file_tail
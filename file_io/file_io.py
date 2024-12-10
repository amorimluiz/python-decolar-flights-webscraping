import json

class FileIO:
  def __init__(self, file_path):
    self.file_path = file_path

  def read_json_file(self):
    with open(self.file_path, 'r') as file:
      return json.load(file)
    
  def exists(self):
    try:
      with open(self.file_path, 'r'):
        return True
    except:
      return False
import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.ogg import OggFileType

class AudioLibraryOrganizer:
    def __init__(self, origin_path, dest_path = None):
        self.origin_path = origin_path
        if dest_path == origin_path:
            return ValueError(f'Destination path cannot be the same as origin path: {dest_path}')
        self.__dest_path = dest_path
        self.origin_struct = None
        self.dest_struct = None
        self.file_name_format = None
        self.tag_map = None
        self.all_tags = None
            
            
            
    def get_file_structure(self, path = 'set_default', set_member = False):
        if path == 'set_default':
            path = self.origin_path
        file_struct = {}
                
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            if os.path.isfile(item_path):
                tags = self.get_file_tags(item_path)
                if type(tags) == str:
                    continue
                #tags['new_path'] = None
                file_struct[item_path] = tags
                
            elif os.path.isdir(item_path):
                print(f'Processing dir: {item_path}')
                file_struct[item_path] = self.get_file_structure(item_path)
        
        if set_member:
            self.origin_struct = file_struct    
        return file_struct
            
            
                
    def get_file_tags(self, full_path, which = 'all'):
        aud_obj = self.get_audio_obj(full_path)
        try:
            tags = aud_obj.tags
            return tags
        except:
            return aud_obj
        
        
    
    def get_audio_obj(self, path):
        filename, ext = os.path.splitext(path)
        
        if ext == '.mp3':
            return MP3(path, ID3 = EasyID3)
        elif ext == '.flac':
            return FLAC(path)
        elif ext == '.m4a':
            return MP4(path)
        elif ext == '.ogg':
            return OGG(path)
        else:
            return f'Incompatible file type: {ext}'
            
            
            
    def get_all_tags(self, struct = False, set_member = False):
        if self.origin_struct == None:
            return 'File structure representation object not created'
        struct = self.origin_struct
        tags = []
                
        for item in struct:
            item_path = os.path.join(self.origin_path, item)
                
            if os.path.isfile(item_path):
                file_tags = [k for k, v in self.get_file_tags(item_path).items() if k not in tags]
                tags.extend(file_tags)
                
            elif os.path.isdir(item_path):
                tags.extend(self.get_all_tags(struct = item))
                
        if set_member:
            self.all_tags = tags
            
        return tags
            
import pprint
bb = 'bad_bunny_un_verano_sin_ti'
kg = 'Mañana Será bonito'
d = os.path.join(os.getcwd())
alo = AudioLibraryOrganizer(d)

alo.get_file_structure(set_member = True)
alo.get_all_tags(set_member = True) 
print(alo.all_tags)

import pprint

def pretty_format(obj):
    pp = pprint.PrettyPrinter(indent=4, width=80, depth=None, compact=False)
    formatted_str = pp.pformat(obj)
    print(formatted_str)

#pretty_format(alo.origin_struct)

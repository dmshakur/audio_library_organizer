import os

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.ogg import OggFileType
import pandas as pd

class AudioLibraryOrganizer:
    def __init__(self, origin_path, dest_path = None):
        self.origin_path = origin_path
        if dest_path == origin_path:
            return ValueError(f'Destination path cannot be the same as origin path: {dest_path}')
        self.origin_df = None
        self.__dest_path = dest_path

        self.all_tags = None
        self.file_name_format = None
        #self.filetype_tag_translator = None
        self.folder_structure = None
        self.tag_case = None
        self.tag_map = None
            
            
            
    def create_origin_dataframe(self, path = 'set_default'):
        if self.all_tags == None:
            return ValueError('self.tags must be initialized before running this method.')
        if path == 'set_default':
            path = self.origin_path

        columns = ['origin_path', 'dest_path', 'type'].extend(self.all_tags)
        df = pd.DataFrame(columns = columns)

        for root, _, files in os.walk(self.origin_path):
            for file in files:
                file_data = {}
                full_file_path = os.path.join(root, file)
                try:
                    file_data = self.get_file_tags(full_file_path)
                    file_data['origin_path'] = full_file_path
                    file_data['type'] = os.path.splitext(full_file_path)[1]
                    appending_df = pd.DataFrame([file_data])
                    appending_df = appending_df.reindex(columns = columns)
                    df = pd.concat([df, appending_df], ignore_index = True)
                except Exception as e:
                    print('Error in create_file_dataframe')
                    print(e)
                    print(file_data)
        self.origin_df = df    
        return df



    def set_dest_path(self, dest_path):
        if destpath == self.origin_path or not os.listdir(destpath):
            print('Destination path cannot be the same as self.origin_path, and the directory musg be empty')
            while dest_path == self.origin_path or not os.listdir(destpath):
                dest_path = input('Enter a new destination path: ')
        self.dest_path = dest_path
        print(f'Destination path set: {dest_path}')
        return dest_path
            
            
                
    def get_file_tags(self, full_path):
        aud_obj = self.get_audio_obj(full_path)
        try:
            tags = dict(aud_obj.tags)
            fixed_tags = {}
            for k, v in tags.items():
                if len(v) == 1:
                    fixed_tags[k] = v[0]
                else:
                    fixed_tags[k] = v
            return fixed_tags
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
            
            
            
    def create_all_tags(self):
        tags = []
        
        for root, _, files in os.walk(self.origin_path):
            for file in files:
                full_file_path = os.path.join(root, file)
                file_tags = self.get_file_tags(full_file_path)
                if type(file_tags) == dict:
                    tags.extend([file_tag for file_tag, _ in file_tags.items() if file_tag not in tags])
                
        self.all_tags = tags
        return tags



    def create_tag_map(self):
        if self.all_tags == None:
            return ValueError('self.all_tags not initialized, value is currently set to None')

        tag_map = {}

        for tag in self.all_tags:
            operation = 'none'
            while operation not in ['delete', 'change', 'keep', 'mimic']:
                operation = input(f'Input operation to do on current tag "{tag}", "delete" "mimic" "change" "keep": ')

            if operation == 'delete':
                tag_map[tag] = operation
            elif operation == 'change':
                unique_tag_check = True
                new_tag = ''
                while unique_tag_check:
                    new_tag = input(f'What tag should "{tag}" be changed to? ')
                    if new_tag not in self.all_tags:
                        cont = input('This tag is not in self.all_tags, continue to change? y/n: ')
                        if cont.lower() == 'y':
                            unique_tag_check = False
                    else:
                        unique_tag_check = False
                tag_map[tag] = new_tag
            elif operation == 'mimic':
                tag_to_mimic = ''
                while tag_to_mimic not in self.all_tags:
                    tag_to_mimic = input('Input name of tag to mimic: ')
                    if tag_to_mimic not in self.all_tags:
                        print(f'Invalid tag must be from the following: {self.all_tags}')
            elif operation == 'keep':
                tag_map[tag] = 'keep'

        self.tag_map = tag_map
        return tag_map



    def create_filename_format(self):
        filename_tags = []
        separator = '?'
        case = ''
        invalid_separators = '/><:"\'\n?*|'
        case_options = {'all_caps', 'all_lower', 'capital_case', 'first_word_cap'}

        while case not in case_options:
            case = input(f'Input the case type that all filenames should have, only the following options are valid, {case_options}: ')

        print(f'From the following tags, select which you would like to appear in filenames and in the order that you want them to appear:\n{", ".join(self.all_tags)}')

        filename_format_validation_check = True

        while filename_format_validation_check:
            input_format = input('Input tags, space separated: ')
            filename_tags = input_format.split(' ')

            if sum([1 for el in filename_tags if el not in self.all_tags]) == 0:
                filename_format_validation_check = False
            else:
                print('Invalid input')

        while separator in invalid_separators:
            separator = input('Choose a character to serve as a separator to be placed in between tags in the filename: ')

        filename_format = self.filename_format = {'separator': separator, 'filename_tags': filename_tags, 'case': case}
        return filename_format



    def create_tag_case_format(self):
        case_options = {'all_caps', 'all_lower', 'capital_case', 'first_word_cap'}
        tag_case = ''

        while tag_case not in case_options:
            tag_case = input(f'Select a case option from one of the following to be used with tag text, {", ".join(case_options)}: ')
        self.tag_case = tag_case
        return tag_case



    def create_folder_structure(self):
        print('Using the following tags choose what tags to sort by for folders, and in the order that you want them.')

        print(', '.join(self.all_tags))

        folder_structure = 'invalid'

        while folder_structure == 'invalid':
            folder_structure = input('Input desired folder structure by tag, space separarated: ').split(' ')
            
            if all(i not in self.all_tags for i in folder_structure):
                folder_structure = 'invalid'
                print('Invalid entry, all elelements must be within self.all_tags')

        self.folder_structure = folder_structure
        return folder_structure



    def create_new_library(self):
        if None in []:
            return ValueError('Cannot run unless all member variables are initialized.')

        


'''
testing the class out with the code below
'''

kg = 'MAÑANA SERÁ BONITO'
d = os.path.join(os.getcwd(), '..', kg)
alo = AudioLibraryOrganizer(d)
alo.create_all_tags()
#alo.create_file_dataframe().to_csv('df.csv')

def pretty_format(obj):
    import pprint
    pp = pprint.PrettyPrinter(indent=4, width=80, depth=None, compact=False)
    formatted_str = pp.pformat(obj)
    print(formatted_str)

import logging
import os
import re
import shutil
import warnings

warnings.filterwarnings('ignore', category = DeprecationWarning)

logging.basicConfig(filename = 'audio_library_organizer.log', level=logging.INFO, format='%(asctime)s \n %(levelname)s \n %(message)s\n')

from mutagen.easyid3 import EasyID3
#from mutagen.flac import FLAC
from mutagen.mp3 import MP3
#from mutagen.mp4 import MP4
#from mutagen.ogg import OggFileType
import pandas as pd

class AudioLibraryOrganizer:
    def __init__(self, origin_path: str, dest_path = None, origin_df = None, all_tags = None, folder_name_format = None, file_format = None, folder_structure = None, tag_case = None, tag_map = None):
        try:
            self.origin_path = eval(origin_path)
            print(f'Origin path set: {self.origin_path}\n')
        except Exception:
            logging.exception(f'origin_path not compatible with eval: {origin_path}\n')
            self.origin_path = origin_path
            print(f'Origin path set: {self.origin_path}\n')
        if dest_path == origin_path:
            return ValueError(f'Destination path cannot be the same as origin path: {dest_path}\n')
        self.origin_df = origin_df or None
        self.__dest_path = dest_path or None
        self.all_tags = all_tags or None
        self.file_format = file_format or None
        #self.filetype_tag_translator = None #For use when using different fike types, as other file types have different tag systems, than mp3
        self.folder_name_format = folder_name_format or None
        self.folder_structure = folder_structure or None
        self.tag_case = tag_case or None
        self.tag_map = tag_map or None
            
            
            
    def create_origin_dataframe(self, path: str = 'set_default'):
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
                    print(e, file_data, full_file_path)
        self.origin_df = df    
        return df



    def set_dest_path(self, dest_path: str):
        try:
            dest_path = eval(dest_path)
        except Exception:
            logging.exception(f'Dest_path not compatible with eval: {dest_path}')
        if dest_path == self.origin_path or len(os.listdir(dest_path)) > 1:
            print('Destination path cannot be the same as self.origin_path, and the directory musg be empty')
            while dest_path == self.origin_path or not os.listdir(dest_path):
                dest_path = input('Enter a new destination path: ')
        self.__dest_path = dest_path
        print(f'Destination path set: {dest_path}')
        return dest_path
            
            
                
    def get_file_tags(self, full_path: str):
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
        
        
    
    def get_audio_obj(self, path: str):
        filename, ext = os.path.splitext(path)
        
        if ext == '.mp3':
            return MP3(path, ID3 = EasyID3)
        elif ext == '.flac':
            return FLAC(path)
        elif ext == '.m4a':
            return MP4(path)
        elif ext == '.ogg':
            return OGG(path)
            


    def create_new_file(self, full_path: str, dest_path: str):
        shutil.copy2(full_path, dest_path)
        aud_obj = self.get_audio_obj(dest_path)

        for tag, op in self.tag_map.items():
            if op == 'delete':
                del aud_obj[tag]
            elif op != 'keep':
                aud_obj[tag] = [op]

        try:
            for tag, _ in aud_obj.tags.items():
                aud_obj[tag] = self.change_case(aud_obj[tag][0], self.tag_case)
            aud_obj.save()
        except Exception:
            logging.exception(f'Error likely due to non-audio file. dest: {dest_path}, origin: {full_path}')

            

    def create_all_tags(self):
        print('\n*********Getting all file tags.')
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
        print('\n*********Creating tag map.')

        if self.all_tags == None:
            return ValueError('self.all_tags not initialized, value is currently set to None')

        tag_map = {}

        for tag in self.all_tags:
            operation = 'none'
            while operation not in ['delete', 'change', 'keep', 'd', 'c', 'k']:
                operation = input(f'Input operation to do on current tag "{tag}", "[d]elete" "[c]hange" "[k]eep": ')

            if operation in ['d', 'delete']:
                tag_map[tag] = operation
            elif operation in ['c', 'change']:
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
            elif operation in ['k', 'keep']:
                tag_map[tag] = 'keep'

        self.tag_map = tag_map
        return tag_map



    def create_filename_format(self):
        print('\n********Creating filename format')
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
        print('\n********Creating Tag case format.')
        case_options = {'all_caps', 'all_lower', 'capital_case', 'first_word_cap'}
        tag_case = ''

        while tag_case not in case_options:
            tag_case = input(f'Select a case option from one of the following to be used with tag text, {", ".join(case_options)}: ')
        self.tag_case = tag_case
        return tag_case



    def create_folder_structure(self):
        print('\n********Creating folder structure.')
        print(f'Using the following tags choose what tags to sort by for folders, and in the order that you want them: {", ".join(self.all_tags)}')
        folder_structure = 'invalid'

        while folder_structure == 'invalid':
            folder_structure = input('Input desired folder structure by tag, space separarated: ').split(' ')
            
            if all(i not in self.all_tags for i in folder_structure):
                folder_structure = 'invalid'
                print('Invalid entry, all elelements must be within self.all_tags')

        self.folder_structure = folder_structure
        return folder_structure



    def create_dest_file_paths(self):
        print('\n********Creating dest file paths.')
        if None in [self.folder_structure, self.filename_format]:
            return ValueError('Neither self.folder_structure or self.filename_format can be None to run this method.')

        df = self.origin_df.copy()
        for index, row in df.iterrows():
            new_file_name = [row[item] for item in self.filename_format['filename_tags']]

            new_file_name = \
                self.filename_format['separator'].join(new_file_name)
            new_file_name = \
                self.change_case(new_file_name, self.filename_format['case']).replace(' ', self.filename_format['separator'])

            file_folder_structure = [row[item] for item in self.folder_structure]
            for idx, folder in enumerate(file_folder_structure):
                formatted_folder = folder.replace(' ', self.folder_name_format['separator'])
                formatted_folder = self.change_case(formatted_folder, self.folder_name_format['case'])
                file_folder_structure[idx] = formatted_folder

            file_dest_path = os.path.join(self.__dest_path, *file_folder_structure, new_file_name)
            df.at[index, 'dest_path'] = file_dest_path

        self.origin_df = df
        return df



    def create_dest_library(self):
        print('\n********Creating dest library.')
        if None in [self.origin_path, self.__dest_path, self.all_tags, self.filename_format, self.folder_structure, self.tag_case, self.tag_map]:
            return ValueError('Cannot run unless all member variables are initialized.')

        for index, row in self.origin_df.iterrows():
            path, file = os.path.split(row['dest_path'])
            if os.path.exists(path):
                self.create_new_file(row['origin_path'], row['dest_path'] + row['type'])
            else:
                os.makedirs(path)
                self.create_new_file(row['origin_path'], row['dest_path'] + row['type'])

        print(f'New library created at: {self.__dest_path}')



    def create_folder_name_format(self, separator = False, case = False):
        print('\n********Creating folder name format')
        if not separator:
            separator = input('Enter folder name separator: ')
        if not case:
            case_options = {'all_caps', 'all_lower', 'capital_case', 'first_word_cap'}
            while case not in case_options:
                case = input(f'Enter case from option, {", ".join(case_options)}: ')
        folder_name_format = {}
        folder_name_format['separator'] = seprator
        folder_name_format['case'] = case
        self.folder_name_format = folder_name_format



    def change_case(self, value: str, case: str):
        if case == 'capital_case':
            match = lambda m: m.group(0).upper()
            return re.sub(
                r'(?<![a-zA-ZàèìòùáéíóúäëïöüãñõÀÈÌÒÙÁÉÍÓÚÄËÏÖÜÃÑÖ])[a-zA-ZàèìòùáéíóúäëïöüãñõÀÈÌÒÙÁÉÍÓÚÄËÏÖÜÃÑÖ]', 
                match, 
                value.lower(), 
                flags=re.UNICODE
            )
        elif case == 'all_caps':
            return value.upper()
        elif case == 'all_lower':
            return value.lower()
        elif case == 'first_word_cap':
            return value[0].capitalize() + value[1:].lower()



    def __call__(self, dest_path = False):
        self.create_all_tags()
        self.create_origin_dataframe()
        self.set_dest_path(dest_path or input('Enter destination path: '))
        self.create_folder_structure()
        self.create_filename_format()
        self.create_tag_case_format()
        self.create_tag_map()
        self.create_folder_name_format(sep, case)
        self.create_dest_file_paths()
        self.create_dest_library()


if __name__ == '__main__':
    audio_library_organizer = AudioLibraryOrganizer(input('Input origin path: '))
    audio_library_organizer()

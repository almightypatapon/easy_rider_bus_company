import json
import re
from datetime import datetime


class EasyRider:
    data_structure = {
        'bus_id': {
            'field': {'type': int, 'required': True, 'errors': 0},
            'format': None},
        'stop_id': {
            'field': {'type': int, 'required': True, 'errors': 0},
            'format': None},
        'stop_name': {
            'field': {'type': str, 'required': True, 'errors': 0},
            'format': {'template': "^([A-Z][a-z]+\\s)+(Road|Avenue|Boulevard|Street)$", 'errors': 0}},
        'next_stop': {
            'field': {'type': int, 'required': True, 'errors': 0},
            'format': None},
        'stop_type': {
            'field': {'type': 'char', 'required': False, 'errors': 0},
            'format': {'template': "^[SOF]?$", 'errors': 0}},
        'a_time': {
            'field': {'type': str, 'required': True, 'errors': 0},
            'format': {'template': "^([0-1]\\d|[2][0-3]):[0-5]\\d$", 'errors': 0}},
    }
    bus_lines = {}

    def __init__(self, json_str):
        self.json_dict = json.loads(json_str)

    @staticmethod
    def is_char(inp):
        return isinstance(inp, str) and len(inp) == 1 and inp.isalpha() or inp == ''

    def field_validation(self):
        for dict_ in self.json_dict:
            for key in self.data_structure:
                if self.data_structure[key]['field']['type'] != 'char' and type(dict_[key]) != self.data_structure[key]['field']['type'] or\
                        self.data_structure[key]['field']['type'] == 'char' and not self.is_char(dict_[key]) or\
                        self.data_structure[key]['field']['required'] and dict_[key] == '':
                    self.data_structure[key]['field']['errors'] += 1

    def format_validation(self):
        for dict_ in self.json_dict:
            for key in self.data_structure:
                if self.data_structure[key]['format']:
                    if not re.match(self.data_structure[key]['format']['template'], dict_[key]):
                        self.data_structure[key]['format']['errors'] += 1

    def get_bus_lines(self):
        for dict_ in self.json_dict:
            if dict_['bus_id'] not in self.bus_lines:
                self.bus_lines[dict_['bus_id']] = [dict_['stop_name']]
            else:
                self.bus_lines[dict_['bus_id']].append(dict_['stop_name'])

    def get_stops_type(self):
        for dict_ in self.json_dict:
            if dict_['bus_id'] not in self.bus_lines:
                self.bus_lines[dict_['bus_id']] = [{dict_['stop_type']: dict_['stop_name']}]
            else:
                self.bus_lines[dict_['bus_id']].append({dict_['stop_type']: dict_['stop_name']})

    def get_stops_time(self):
        for dict_ in self.json_dict:
            if dict_['bus_id'] not in self.bus_lines:
                self.bus_lines[dict_['bus_id']] = [{dict_['stop_name']: dict_['a_time']}]
            else:
                self.bus_lines[dict_['bus_id']].append({dict_['stop_name']: dict_['a_time']})

    def stops_validation(self):
        all_stops = {'Start stops': [], 'Transfer stops': [], 'Finish stops': [], 'All stops': {}}
        for key in self.bus_lines:
            s_stops, f_stops, t_stops = [], [], []
            for stop in self.bus_lines[key]:
                if key not in all_stops['All stops'].keys():
                    all_stops['All stops'][key] = [list(stop.values())[0]]
                else:
                    all_stops['All stops'][key].append(list(stop.values())[0])
                if 'S' in stop:
                    if not s_stops:
                        s_stops.append(list(stop.values())[0])
                        all_stops['Start stops'].append(list(stop.values())[0])
                    else:
                        print(f'There is more then one starting point for the line: {key}.')
                        break  # exit()
                elif 'F' in stop:
                    if not f_stops:
                        f_stops.append(list(stop.values())[0])
                        all_stops['Finish stops'].append(list(stop.values())[0])
                        if 'Sesame Street' in stop.values():
                            all_stops['Transfer stops'].append(list(stop.values())[0])
                    else:
                        print(f'There is more then one final stop for the line: {key}.')
                        break  # exit()
            if not s_stops or not f_stops:
                print(f'There is no start or end stop for the line: {key}.')
                break  # exit()

        all_ = []
        for key, values in all_stops['All stops'].items():
            for value in values:
                all_.append(value)

        for s in all_:
            counter = 0
            for key, values in all_stops['All stops'].items():
                if s in values:
                    counter += 1
            if counter > 1:
                all_stops['Transfer stops'].append(s)

        for key, value in all_stops.items():
            if key != 'All stops':
                value = set(value)
                value = list(value)
                value.sort()
                # print(f'{key}: {len(value)} {value}')

        print('On demand stops test:')
        wrong = []
        for value in self.bus_lines.values():
            for stop in value:
                for type_, name in stop.items():
                    if type_ == 'O' and name in (all_stops['Start stops'] + all_stops['Transfer stops'] + all_stops['Finish stops']):
                        wrong.append(name)
        if wrong:
            wrong.sort()
            print(f'Wrong stop type: {wrong}')
        else:
            print('OK')

    def time_validation(self):
        print('Arrival time test:')
        errors = 0
        for key in self.bus_lines:
            previous_stop_time = None
            for stop in self.bus_lines[key]:
                stop_name = list(stop.keys())[0]
                stop_time = datetime.strptime(list(stop.values())[0], '%H:%M')
                if previous_stop_time:
                    if stop_time < previous_stop_time:
                        print(f'bus_id line {key}: wrong time on station {stop_name}')
                        errors += 1
                        break
                previous_stop_time = stop_time
        if errors == 0:
            print('OK')

    def print_field_errors(self):
        print('Type and required field validation:',
              sum(self.data_structure[key]['field']['errors'] for key in self.data_structure), 'errors')
        for key in self.data_structure:
            print(key + ':', self.data_structure[key]['field']['errors'])

    def print_format_errors(self):
        print('Format validation:',
              sum(self.data_structure[key]['format']['errors'] for key in self.data_structure if self.data_structure[key]['format']), 'errors')
        for key in self.data_structure:
            if self.data_structure[key]['format']:
                print(key + ':', self.data_structure[key]['format']['errors'])

    def print_bus_lines(self):
        print('Line names and number of stops:')
        for key in self.bus_lines:
            print(f'bus_id: {key}, stops: {len(set(self.bus_lines[key]))}')

    def print_bus_lines_dict(self):
        for key in self.bus_lines:
            print(f'bus_id: {key}, stops: {self.bus_lines[key]}')


input_ = '''
[{"bus_id" : 128,
 "stop_id" : 1,
 "stop_name" : "Prospekt Avenue",
 "next_stop" : 3,
 "stop_type" : "S",
 "a_time" : "08:12"},
 {"bus_id" : 128,
 "stop_id" : 3,
 "stop_name" : "Elm Street",
 "next_stop" : 5,
 "stop_type" : "",
 "a_time" : "08:19"},
 {"bus_id" : 128,
 "stop_id" : 5,
 "stop_name" : "Fifth Avenue",
 "next_stop" : 7,
 "stop_type" : "O",
 "a_time" : "08:17"},
 {"bus_id" : 128,
 "stop_id" : 7,
 "stop_name" : "Sesame Street",
 "next_stop" : 0,
 "stop_type" : "F",
 "a_time" : "08:07"},
 {"bus_id" : 256,
 "stop_id" : 2,
 "stop_name" : "Pilotow Street",
 "next_stop" : 3,
 "stop_type" : "S",
 "a_time" : "09:20"},
 {"bus_id" : 256,
 "stop_id" : 3,
 "stop_name" : "Elm Street",
 "next_stop" : 6,
 "stop_type" : "",
 "a_time" : "09:45"},
 {"bus_id" : 256,
 "stop_id" : 6,
 "stop_name" : "Sunset Boulevard",
 "next_stop" : 7,
 "stop_type" : "",
 "a_time" : "09:44"},
 {"bus_id" : 256,
 "stop_id" : 7,
 "stop_name" : "Sesame Street",
 "next_stop" : 0,
 "stop_type" : "F",
 "a_time" : "10:12"},
 {"bus_id" : 512,
 "stop_id" : 4,
 "stop_name" : "Bourbon Street",
 "next_stop" : 6,
 "stop_type" : "S",
 "a_time" : "08:13"},
 {"bus_id" : 512,
 "stop_id" : 6,
 "stop_name" : "Sunset Boulevard",
 "next_stop" : 0,
 "stop_type" : "F",
 "a_time" : "08:16"}]
'''

easy_rider = EasyRider(input())
easy_rider.get_stops_type()
easy_rider.stops_validation()

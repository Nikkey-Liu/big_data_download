#!/bin/python

import os
from bs4 import BeautifulSoup
import lxml
import numpy as np
import pandas as pd

def extract_week(input=''):
    # extract weeks into an array
    output = []
    splitted_by_comma = input.split(',')
    for value in splitted_by_comma:
        if '-' in value:
            splitted_by_dash = value.split('-')
            for val in range(int(splitted_by_dash[0]), int(splitted_by_dash[1])+1):
                output.append(val)
        else:
            output.append(int(value))

    return output

def add_entry(array=[], output={}):
    # updates the ouput dict with the array
    module_type = str(array[3]).split(' - ')
    module_time = array[2].split(' - ')

    if len(module_type) == 2:
        output['module_code'].append(module_type[0])
        output['lec_type'].append(module_type[1])
    elif len(module_type) == 3:
        output['module_code'].append(module_type[0])
        output['lec_type'].append(f'{module_type[1]} - {module_type[2]}')
    else:
        output['module_code'].append(module_type[0])
        output['lec_type'].append('-')

    output['year'].append(array[0])
    output['course_title'].append(array[1])
    output['module_start_time'].append(module_time[0])
    output['module_end_time'].append(module_time[1])
    output['lecturer'].append(array[4])
    output['lec_room'].append(array[5])
    output['week'].append(extract_week(array[6]))
    output['day_of_the_week'].append(array[7])

def get_module_details(file=''):
    # returns a dict containing course, module & lecture details
    modules_details = {'year':[], 'course_title':[], 'module_start_time':[], 'module_end_time':[],
        'module_code':[], 'lec_type':[], 'lecturer':[], 'lec_room':[], 'week':[],
        'day_of_the_week': []}
    with open(file, 'r') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')
        list_div = soup.find('div', class_='BOX')
        if list_div != None:
            list_div = list_div.find_all('select')
            course_year = list_div[0].find('option', attrs={'selected': 'selected'}).text
            course_title = list_div[1].find('option', attrs={'selected': 'selected'}).text
            table_row_list = soup.find('table').find_all('tr')[1:]
            for row in table_row_list:
                td_list= row.find_all('td')
                days_of_the_week = ['monday', 'tuesday', 'wednesday', 'thursday',
                            'friday', 'saturday']
                for index, td in enumerate(td_list):
                    day = days_of_the_week[index]
                    contents = td.contents[0].contents
                    contents = list(filter((' ').__ne__, contents))
                    # convert the br tag object to str then remove it
                    for index, val in enumerate(contents):
                        if type(val) != str:
                            contents[index] = str(val)
                    contents = list(filter(('<br/>').__ne__, contents))
                    length = len(contents)
                    lim = 5
                    no_courses = int(length/lim)
                    for i in range(0,no_courses):
                        if i == 0:
                            start = 0
                        end = start + lim
                        concat = [course_year, course_title] + contents[start:end] + [day]
                        add_entry(concat, modules_details)
                        start = end

    return modules_details



if __name__ == '__main__':
    print('Start cleaning html files!')
    for course_id in range(1,1001,1):
        for year in range(1,6):
            if course_id < 100:
                filename= f'data/LM0{course_id}{year}.html'
            else:
                filename = f'data/LM{course_id}{year}.html'
            csv = f'output/{filename[5:-5]}.csv'

            omit = ['0281', '0291', '0381', '0391', '0401', '0924',
             '0444', '0501', '0522', '0532', '0541', '0552', '0561',
             '0714', '0734', '0774', '0891', '0901', '0923', '0963']
            if filename[7:-5] in omit:
                break

            if os.path.isfile(filename) and os.path.isfile(csv) == False:
                print(filename)
                df = pd.DataFrame(get_module_details(filename))
                df.to_csv(csv, index=False)
                print(csv)

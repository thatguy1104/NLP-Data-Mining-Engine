import json

def test_module_number():
    with open('all_module_links.json') as json_file:
        data = json.load(json_file)
        counter_1 = 0
        for i in data:
            # print(data[i]['Department_ID'], data[i]['Department_Name'])
            if data[i]['Department_ID'] == 'COMPS_ENG':
                counter_1 += 1

    with open('CS_courses.json') as json_file:
        data = json.load(json_file)['modules']
        counter_2 = 0

        for i in data:
            counter_2 += 1
        
    assert counter_1 == counter_2, "Number of modules does not match"



test_module_number()

import os
import re
from xml.dom.minidom import parse, Node
import json
import time

def start() -> None:
    dir = ''

    while True:
        dir = input("Enter directory with XML files:")
        if (os.path.isdir(dir)):
            break
        else:
            print('Sorry, directory name is invalid. Try one more time')

    os.mkdir('./results')

    filename_pattern = re.compile("^.*\.xml$")

    for (dirpath, dirnames, filenames) in os.walk(dir):
        for filename in filenames:
            if (filename_pattern.match(filename)):
                file_path = os.path.join(dir, filename)
                handleTickets(parse(file_path))
                print(f'Parsed {filename}')


def handleTickets(doc: str) -> None:
    tickets_list = doc.getElementsByTagName('helpdesk-tickets')

    if (len(tickets_list) != 1):
        if (len(tickets_list) == 0):
            print('Error: no one helpdesk-ticket')
        else:
            print('Error: too many helpdesk-tickets')

        return []

    tickets = tickets_list[0].getElementsByTagName('helpdesk-ticket')

    for ticket in tickets:
        if (get_child_element_data_by_tag_name(ticket, 'spam') == 'true'):
            continue

        ticket_dict = {}

        ticket_dict['description'] = get_child_element_data_by_tag_name(ticket, 'description')
        ticket_dict['created_at'] = get_child_element_data_by_tag_name(ticket, 'created-at')
        ticket_dict['subject'] = get_child_element_data_by_tag_name(ticket, 'subject')
        ticket_dict['ticket_type'] = get_child_element_data_by_tag_name(ticket, 'ticket-type')
        ticket_dict['priority'] = get_child_element_data_by_tag_name(ticket, 'priority-name')

        ticket_dict['answers'] = []

        ticket_answers_element = ticket.getElementsByTagName('notes')

        if (len(ticket_answers_element) == 1):
            for note in ticket_answers_element[0].getElementsByTagName('helpdesk-note'):
                answer_dict = {}

                answer_dict['incoming'] = get_child_element_data_by_tag_name(note, 'incoming')
                answer_dict['text'] = get_child_element_data_by_tag_name(note, 'body')

                ticket_dict['answers'].append(answer_dict)

        ticket_id = get_child_element_data_by_tag_name(ticket, 'id')

        file = open(f"./results/{ticket_id}.json", "x")
        file.write(json.dumps(ticket_dict))
        file.close()


def get_child_element_data_by_tag_name(parent_element: Node, tag_name: str) -> str:
    elements_list = parent_element.getElementsByTagName(tag_name)

    if (len(elements_list) == 0):
        print(f'Error: no one {tag_name}')

    elements_len = len(elements_list[0].childNodes)

    if (elements_len != 1):
        if (elements_len == 0):
            pass
            # print(f'Error: no content in {tag_name} in parent {parent_element.tagName}')
        else:
          print(f'Error: too much child elements {tag_name} in parent {parent_element.tagName} : {elements_len} elements')

        return ''

    return elements_list[0].childNodes[0].data


time_start = time.perf_counter()
start()
time_end = time.perf_counter()
time_duration = time_end - time_start
print(f'Took {time_duration:.3f} seconds')
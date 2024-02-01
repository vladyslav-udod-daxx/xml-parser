import os
import re
from xml.dom.minidom import parse, Node
import json
import time

results_count = 0

def start() -> None:
    dir = ''

    while True:
        dir = input("Enter directory with XML files:")
        if (os.path.isdir(dir)):
            break
        else:
            print('Sorry, directory name is invalid. Try one more time')

    os.mkdir('./results')

    for (dirpath, dirnames, filenames) in os.walk(dir):
        for filename in filenames:
            if (filename.endswith('.xml')):
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

    ticket_elements = tickets_list[0].getElementsByTagName('helpdesk-ticket')

    for ticket in ticket_elements:
        if (check_if_ticket_is_useless(ticket)):
            continue

        ticket_dict = {}

        ticket_dict['description'] = remove_whitespaces(get_child_element_data_by_tag_name(ticket, 'description'))
        ticket_dict['created_at'] = get_child_element_data_by_tag_name(ticket, 'created-at')
        ticket_dict['subject'] = get_child_element_data_by_tag_name(ticket, 'subject')
        ticket_dict['ticket_type'] = get_child_element_data_by_tag_name(ticket, 'ticket-type')
        ticket_dict['priority'] = get_child_element_data_by_tag_name(ticket, 'priority-name')

        ticket_dict['answers'] = []

        ticket_answers_element = ticket.getElementsByTagName('notes')

        if (len(ticket_answers_element) == 1):
            note_elements = ticket_answers_element[0].getElementsByTagName('helpdesk-note')

            for note in note_elements:
                if (check_if_note_is_useless(note)):
                    continue

                answer_dict = {}

                answer_dict['incoming'] = get_child_element_data_by_tag_name(note, 'incoming')
                answer_dict['text'] = remove_jira_additions(
                    remove_whitespaces(
                        get_child_element_data_by_tag_name(note, 'body')
                    )
                )

                ticket_dict['answers'].append(answer_dict)

        # ticket without answers is useless
        if (len(ticket_dict['answers']) == 0):
            continue

        ticket_id = get_child_element_data_by_tag_name(ticket, 'id')

        file = open(f"./results/{ticket_id}.json", "x")
        file.write(json.dumps(ticket_dict))
        file.close()

        global results_count
        results_count += 1

def check_if_ticket_is_useless(ticket_element: Node) -> bool:
    if (get_child_element_data_by_tag_name(ticket_element, 'spam') == 'true'):
        return True

    description = get_child_element_data_by_tag_name(ticket_element, 'description')
    if (
        description.startswith('This is an automated ticket') or
        check_if_sting_contain_only_links(description)
    ):
        return True

    subject = get_child_element_data_by_tag_name(ticket_element, 'subject')
    if ((description == '' and subject == '') or (description == 'Not given.' and subject == '')):
        return True

    return False

def check_if_note_is_useless(note_element: Node) -> bool:
    source = get_child_element_data_by_tag_name(note_element, 'source')

    # notes with this source == 4 contain only creation time
    # notes with this source == 15 contain only iformation that ticket is answered
    if (source == '4' or source == '15'):
        return True

    answer_text = get_child_element_data_by_tag_name(note_element, 'body')
    if (
        answer_text == '' or
        answer_text.startswith('Jira issue status changed to') or
        answer_text.startswith('Conversation between') or
        check_if_sting_contain_only_links(answer_text)
    ):
        return True

    return False

def check_if_sting_contain_only_links(sting: str) -> bool:
    return all((x.startswith('http://') or x.startswith('https://')) for x in sting.split(' '))

def remove_whitespaces(string: str) -> str:
    return re.sub(
        r"\s+",
        ' ',
        string
          .replace('\\n', ' ')
          .replace('\n', ' ')
          .replace('\u00a0', ' ')
          .replace('\u200b', ' ')
          .replace('\u2013', ' '),
        flags=re.UNICODE
    )

def remove_jira_additions(string: str) -> str:
    return string.replace('Comment from Jira - ', '').replace(' added this comment', '')

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
print(f'Created {results_count} tickets')
import json
import requests

name = "stoqo_zendesk"

DUMMY_UUID = '00000000-00000000-00000000-00000000'
DUMMY_STORE_NAME = 'STOQO Tester'


class Zendesk():
    _JSON_HEADER = {'content-type': 'application/json'}
    _BINARY_HEADER = {'content-type': 'application/binary'}
    _BASE_URL = f'https://stoqo.zendesk.com/api/v2'

    def __init__(self, email, token, dev=False):
        self.auth = (f'{email}/token', token)
        self.dev_mode = dev

    def get_or_create_user(self, store_id, store_name):
        if self.dev_mode:
            store_id = DUMMY_UUID
            store_name = DUMMY_STORE_NAME

        url = f'{self._BASE_URL}/users/search.json?external_id={store_id}'
        response = requests.get(url, auth=self.auth)
        self._validate_response(response, 200)

        data = response.json()
        if data['count'] == 0:
            return self._create_user(store_id, store_name)
        return data['users'][0]

    def get_tickets(self, user_id):
        url = f'{self._BASE_URL}/users/{user_id}/tickets/requested.json'
        response = requests.get(url, auth=self.auth)
        self._validate_response(response, 200)

        return response.json()['tickets']

    def create_ticket(self, user_id, subject, description, custom_fields, attachment_token=None):
        comment = {'body': description}
        if attachment_token:
            comment['uploads'] = [attachment_token]

        payload = json.dumps({
            'ticket': {
                'subject': subject,
                'comment': comment,
                'custom_fields': custom_fields,
                'requester_id': user_id,
            }
        })
        url = f'{self._BASE_URL}/tickets.json'
        headers = self._JSON_HEADER

        response = requests.post(url, data=payload, auth=self.auth, headers=headers)
        self._validate_response(response, 201)

        return response.json()['ticket']

    def get_ticket_fields(self):
        url = f'{self._BASE_URL}/ticket_fields.json'
        response = requests.get(url, auth=self.auth)
        self._validate_response(response, 200)

        return response.json()['ticket_fields']

    def upload_file(self, file, token):
        '''See README on how to use this method properly'''
        url = f'{self._BASE_URL}/uploads.json?filename={file.name}'
        if token:
            url = f'{url}&token={token}'
        headers = self._BINARY_HEADER

        response = requests.post(url, data=file, auth=self.auth, headers=headers)
        self._validate_response(response, 201)

        return response.json()['upload']

    def flatten_ticket_custom_fields(self, tickets):
        '''Flatten ticket's custom fields to be easily consumed'''
        result = []
        for ticket in tickets:
            custom_fields = ticket['custom_fields']
            result.append({
                'id': ticket['id'],
                'status': ticket['status'],
                'order_id': self._find_value_by_id(custom_fields, 360015380794),
                'delivery_date': self._find_value_by_id(custom_fields, 360015384053),
                'report_date': ticket['created_at'],
                'decision_date': self._find_value_by_id(custom_fields, 360015384673),
                'type': self._find_value_by_id(custom_fields, 360015390013),
                'category': self._find_value_by_id(custom_fields, 360015341793),
                'subcategory': self._find_value_by_id(custom_fields, 360016595493),
                'subject': ticket['subject'],
                'action': self._find_value_by_id(custom_fields, 360015422174),
                'description': ticket['description'],
                'sku_with_quantity': self._find_value_by_id(custom_fields, 360015384213),
            })
        return result

    def _create_user(self, external_id, user_name):
        payload = json.dumps({
            'user': {
                'name': user_name,
                'verified': True,
                'external_id': str(external_id),
            }
        })
        url = f'{self._BASE_URL}/users.json'
        headers = self._JSON_HEADER

        response = requests.post(url, data=payload, auth=self.auth, headers=headers)
        self._validate_response(response, 201)

        return response.json()['user']

    @staticmethod
    def _find_value_by_id(fields, desired_id):
        return next((item['value'] for item in fields if item['id'] == desired_id), None)

    @staticmethod
    def _validate_response(response, expected_status_code):
        if response.status_code != expected_status_code:
            raise Exception(f'Error {response.status_code}: {response.content}')

# STOQO Zendesk Wrapper

This library is a thin wrapper with standardized interface for interacting with Zendesk to use across all STOQO services. Specifically, the purpose is to:

1. Ease our interfacing and maintain data consistency across our services.
2. Achieve all use cases we need to handle while maintaining simplicity.

## Installation Instructions

Elastic Beanstalk SSH access keys needs to be configured before we can install package from private repository using `pip`. Make sure that `.ebextensions/private-pip-ssh-keys.config` exists in your repository, else consult your backend team. After that, add the following line to `requirements.txt` then run `pip instal -r requirements.txt`

```
git+ssh://git@bitbucket.org/stoqo/stoqo-zendesk@master#egg=stoqo-zendesk
```

```python
from stoqo_zendesk import Zendesk

zendesk_client = Zendesk(email, password)

# If you are in local dev environment, set dev to True. This will prevent us from polluting our production data.
zendesk_client = Zendesk(email, password, dev=True)
```

## Usage

### Get or create user

```python
zendesk_client.get_or_create_user(store_id, store_name)
```

We are storing `Store` in Zendesk as end-users in Zendesk, hence the `user` nomenclature. This method will return complete Zendesk user by retrieving existing one or creating it if it's not on Zendesk yet. Most of the time we will only need the `id` attribute. **To maintain interoperability between our services, the "primary key" used will be store ID in main API.**

### Get tickets of a user

```python
zendesk_client.get_tickets(user_id)
```

After we have Zendesk user ID, we can use this method to retrieve all tickets for a particular store.

### Create ticket on behalf of user

```python
zendesk_client.create_ticket(self, user_id, subject, description, custom_fields)
```

Subject and description are mandatory informations required for a ticket. Custom fields are user-defined fields (by Rizal to be precise) that contains all additional values for a ticket. It is a list of dicts that contains any fields we need to attach to a ticket. For example:

```python
custom_fields = [
    {
        "id": 360015380794,  # Order ID
        "value": "40ffea27-d448-4c2e-8c57-ee3e9c6630ff"
    },
    {
        "id": 360015341793,  # Category
        "value": "sku"
    },
    {
        "id": 360015422174,  # Outlet CX decision
        "value": "rescue_-_pengantaran_barang"
    },
    {
        "id": 360015384053,  # Delivery date
        "value": "2019-03-05"
    }
]
```

In order to get the custom fields IDs and possible values we can use method below.

### Get ticket fields

```python
zendesk_client.get_ticket_fields()
```

Word of caution though: this method will return a large list of dictionaries containing all custom fields that we have defined including all of its properties, so you may need to filter it before passing it to end-user app.

### Upload files

```python
# Example of usage for Django
class TicketFileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename):
        token = request.query_params.get('token', None)
        token = zendesk_client.upload_file(request.data['file'], token)['token']
        return Response({'token': token})
```

This method is only tested using Django's File interface. It should contain the raw data and the filename. If you are uploading more than 1 file for a single ticket, you may supply token that you received from uploading the first file.

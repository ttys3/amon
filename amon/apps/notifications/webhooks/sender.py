import logging
import requests
import json
from dingtalkchatbot.chatbot import DingtalkChatbot

logger = logging.getLogger(__name__)

'''
xiaoding.send_markdown(title='amon警报', text='#### Server:web1 Disk<80% for 30.0 minutes  (Current value: vda1/24.71%)\n'
                           '> ###### server: {"name": "web1"}\n\n'
                           '> ###### trigger: {"from": 13988886666, "average_value": 24.71, "to": 13988886666}\n\n'
                           '> ###### alert: {"key": null, "above_below": "below", "rule_type": "system", "period": 1800, "metric": "Disk", "metric_value": 80, "metric_type": "%"}\n\n',
                           is_at_all=True)
'''

def _send_webhook(auth=None, data=None):
    url = auth.get('url')
    secret = auth.get('secret')

    if secret:
        data['secret'] = secret

    #data = json.dumps(data)
    xiaoding = DingtalkChatbot(url)
    error = None
    try:
        #r = requests.post(url, data=data, timeout=5)
        if 'server' not in data:
            print("sending tests ...")
            xiaoding.send_text(msg=json.dumps(data), is_at_all=False)
        else:
            print("sending notification ...")
            xiaoding.send_markdown(title= 'amon警报: %s' %(data['message']), text='#### {message} \n'
                                       '> ###### server: {server_name}\n\n'
                                       '> ###### trigger: {trigger}\n\n'
                                       '> ###### alert: {alert}\n\n'.format(message=data['message'], server_name=data['server']['name'], trigger=data['trigger'], alert=data['alert']),
                                       is_at_all=True)
    except Exception as e:
        logger.exception('Can not send webhook: {0}'.format(e))
        error = e

    return error

def generate_webhook_data(notification=None, message=None):
    hook_values = {
        'server': ['name'],
        'custom_metric': ['name'],
        'process': ['name'],
        'plugin': ['name'],
        'trigger': ['from', 'average_value', 'time'],
        'alert': ['rule_type', 'metric', 'period','metric_type', 'metric_value', 'above_below', 'key']
    }

    beautify_names = {
        'trigger': {'time': 'to'}
    }

    values = notification.__dict__
    hook_data = {}
    for key, values_list in hook_values.items():
        value = values.get(key, False)
        name_dict = beautify_names.get(key, {})
        
        if value:
            hook_data[key] = {}
            
            for inner_key in values_list:
                new_key = name_dict.get(inner_key, inner_key) # Get or default

                hook_data[key][new_key] = value.get(inner_key)

    hook_data['message'] = message

    return hook_data


def send_webhook_notification(notification=None, auth=None, message=None):
    sent = False
    

    if auth != None and notification.mute == False:
        hook_data = generate_webhook_data(notification=notification, message=message)
        
        _send_webhook(auth=auth, data=hook_data)

    return sent

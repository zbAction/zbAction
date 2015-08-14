from datetime import datetime
from textwrap import dedent

from secrets import secrets

def log(*args):
    template = '''
        Timestamp: {timestamp}
        Message:
        {message}
    '''

    template = dedent(template)
    template = template.format(
        timestamp=datetime.utcnow(),
        message='\t' + '\n\t'.join(map(lambda x: str(x), args))
    )

    print template

    with open(secrets.output_log, 'a') as f:
        f.write(template)

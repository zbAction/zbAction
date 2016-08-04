from datetime import datetime
from fcntl import lockf, LOCK_EX, LOCK_UN
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

    with open(secrets.output_log, 'a') as f:
        lockf(f, LOCK_EX)

        print template
        f.write(template)

        lockf(f, LOCK_UN)

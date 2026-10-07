import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'instance', 'campus.db')


def main():
    if not os.path.isfile(DB_PATH):
        raise SystemExit('Database not found: %s' % DB_PATH)

    with sqlite3.connect(DB_PATH) as connection:
        columns = {
            row[1]
            for row in connection.execute('PRAGMA table_info(chat_message)')
        }
        if not columns:
            raise SystemExit('chat_message table not found')

        if 'source_doc' not in columns:
            connection.execute(
                'ALTER TABLE chat_message ADD COLUMN source_doc TEXT'
            )
            print('Added chat_message.source_doc.')
        else:
            print('chat_message.source_doc already exists.')


if __name__ == '__main__':
    main()

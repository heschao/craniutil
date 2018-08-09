from nose.tools import set_trace
import logging
import tempfile
from typing import List

import postgres_copy
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from craniutil.dbtest.testdb import TestDb

logger = logging.getLogger(__name__)


def copy_postgres(cls, session, filename):
    with open(filename) as fp:
        flags = {'format': 'csv', 'header': True}
        postgres_copy.copy_from(fp, cls, session.connection(), **flags)


def to_tempfile(x: List[List]):
    with tempfile.NamedTemporaryFile(delete=False,mode='w') as tf:
        for row in x:
            tf.write(','.join([str(z) for z in row]))
            tf.write('\n')

    logger.info('wrote {:} rows to temp file {:}'.format(len(x), tf.name))
    return tf.name


class BulkUploadException(Exception):
    pass


def bulk_upload(cls, session, table_data: List[List]):
    header = table_data[0]
    cols = [column.name for column in cls.__mapper__.columns if isinstance(column, Column)]
    assert len(header) == len(cols)
    for i in range(len(header)):
        assert header[i] == cols[i]
    dialect = session.connection().dialect.name
    if dialect == 'postgresql':
        filename = to_tempfile(table_data)
        copy_postgres(cls=cls, session=session, filename=filename)
    else:
        raise BulkUploadException('unknown dialect {}'.format(dialect))


Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'
    name = Column(String, primary_key=True)
    age = Column(Integer)


class TestCopy(TestDb):
    @classmethod
    def base(cls):
        return Base

    def test_copy(self):
        try:
            assert self.session.query(Person).count() == 0
            data = [
                ['name', 'age'],
                ['chao', 45],
                ['jen', 46]
            ]
            bulk_upload(Person, self.session, data)
            assert self.session.query(Person).count() == 2
        finally:
            self.session.rollback()

import datetime
import sqlalchemy
from pythonfosdem.models import Event
from pythonfosdem.extensions import db
from .common import PFTestCase

class EventTestCase(PFTestCase):
    def test_create_event_error(self):
        with self.app.test_request_context():
            # There is no name for the event, raise an exception
            with self.assertRaises(sqlalchemy.exc.IntegrityError):
                event = Event()
                db.session.add(event)
                db.session.commit()

            # Reset the current transaction
            db.session.rollback()
            with self.assertRaises(ValueError):
                event = Event(
                    name='Python FOSDEM 2014',
                    stop_on=datetime.date(2014, 1, 31),
                    start_on=datetime.date(2014, 2, 2),
                    duedate_start_on=datetime.date(2013, 11, 17),
                    duedate_stop_on=datetime.date(2013, 12, 15)
                )
                db.session.add(event)
                db.session.commit()

    def test_current_event(self):
        with self.app.test_request_context():
            event = Event(
                name='Python FOSDEM 2014',
                start_on=datetime.date(2014, 1, 31),
                stop_on=datetime.date(2014, 2, 2),
                duedate_start_on=datetime.date(2013, 11, 17),
                duedate_stop_on=datetime.date(2013, 12, 15)
            )
            db.session.add(event)

            event = Event(
                name='Python FOSDEM 2013',
                start_on=datetime.date(2013, 1, 31),
                stop_on=datetime.date(2013, 2, 2),
                duedate_start_on=datetime.date(2012, 11, 17),
                duedate_stop_on=datetime.date(2012, 12, 15),
                active=False
            )
            db.session.add(event)
            db.session.commit()

            event = Event.current_event()
            self.assertEqual(event.name, 'Python FOSDEM 2014')
            self.assertEqual(event.start_on, datetime.date(2014, 1, 31))
            self.assertEqual(event.stop_on, datetime.date(2014, 2, 2))
            self.assertEqual(event.duedate_start_on, datetime.date(2013, 11, 17))
            self.assertEqual(event.duedate_stop_on, datetime.date(2013, 12, 15))
            self.assertTrue(event.active)



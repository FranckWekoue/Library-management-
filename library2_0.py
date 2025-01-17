import unittest
from datetime import datetime, timedelta
from Library2_0 import Library, PhysicalBook

class TestLibrary(unittest.TestCase):
    def setUp(self):
        # first we need to create our testing environment with the basics
        self.library = Library()
        self.book = PhysicalBook("Test Book", "Author", "B001", "Shelf A")
        self.library.add_book(self.book)
        self.library.create_membership("Test Member")
        self.member = self.library.members["Test Member"]
        self.member.membership_active = True

    def test_borrow_book(self):
        initial_time = datetime.now()
        self.member.borrow_book(self.book)
        
        self.assertIn(self.book, self.member.borrowed_books)
        
        # Now we need to make sure the due date is exactly 7 days later
        # But since computers take time to run code, we give it a 1-second wiggle room
        expected_due_date = initial_time + timedelta(days=7)
        actual_due_date = self.book.due_date
        difference = abs((actual_due_date - expected_due_date).total_seconds())
        self.assertLess(difference, 1, "Due date should be within 1 second of expected time")

    def test_return_book(self):
        # We need to borrow the book first because obviously you can't return what you haven't borrowed
        self.member.borrow_book(self.book)
        self.member.return_book(self.book)
        
        self.assertNotIn(self.book, self.member.borrowed_books)
        self.assertIsNone(self.book.due_date)   #This is important because when a book is returned, you want to make sure all borrowing-related data is properly cleared. Setting the due date to None indicates that the book is no longer checked out to anyone

    def test_create_membership(self):
        self.assertIn("Test Member", self.library.members)
        member = self.library.members["Test Member"]
        
        # Then we make sure our new member is set up correctly with all the defaults
        self.assertEqual(member.name, "Test Member")
        self.assertTrue(member.membership_active)
        self.assertEqual(len(member.borrowed_books), 0)

    def test_study_room_reservation(self):
        self.library.reserve_study_room("Room 101", "Test Member", 2)
        
        self.assertIn("Room 101", self.library.study_rooms)
        reservations = self.library.study_rooms["Room 101"]
        
        # We need to make sure the reservation is formatted properly with the time slots
        self.assertEqual(len(reservations), 1)
        self.assertIn("Test Member", reservations[0])
        self.assertIn(":", reservations[0])

    def test_fine_calculation(self):
        # Now we're going to test if the fines add up correctly over multiple late returns
        self.library.calculate_fine(self.member, overdue_days=3)
        expected_fine = 3 * Library.LATE_FEE_PER_DAY
        self.assertEqual(self.library.fines[self.member], expected_fine)
        
        self.library.calculate_fine(self.member, overdue_days=2)
        self.assertEqual(self.library.fines[self.member], expected_fine + (2 * Library.LATE_FEE_PER_DAY))

if __name__ == "__main__":
    unittest.main()

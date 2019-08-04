import unittest
from Utility import *


# Class to test the Utility functions
# There may be a delay at the beginning of the test as the
# connection is being established
class Test(unittest.TestCase):

    # Setting up a single connection & cursor for all test cases
    @classmethod
    def setUpClass(cls):
        cls.cnx = est_connection()
        cls.cursor = cls.cnx.cursor()

    # Close the connection and cursor
    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.cnx.close()

    # Verify the pk for a particular row can be found
    def test_get_pk_city(self):
        city_id_a = get_pk(self.cursor, "city", "city_name", "Boston", "city_id")
        self.assertEqual(1, city_id_a)
        city_id_b = get_pk(self.cursor, "city", "city_name", "boston", "city_id")
        self.assertEqual(1, city_id_b)

    # Verify a pk of any place of the given type can be found
    # Used when checking if a type should be deemed valid for a certain category
    def test_get_pk_type(self):
        type_pk = get_pk(self.cursor, 'place', 'type', 'American', 'place_id', 'dining')
        self.assertIsNotNone(type_pk)

    # Verify the pk for a feature related to a category can be found
    def test_get_feature_pk(self):
        feature_id_a = get_feature_pk(self.cursor, 'dining', 'accepts reservations')
        self.assertEqual(56, feature_id_a)
        feature_id_b = get_feature_pk(self.cursor, 'museum', 'good for kids')
        self.assertEqual(53, feature_id_b)

    # Verify that the types of a category can be sampled
    def test_sample_types(self):
        types = sample_types(self.cursor, 'dining')
        expected = [('American', 43),
                    ('Restaurant', 43),
                    ('Italian', 27),
                    ('Seafood', 25),
                    ('Pizza', 18)]
        self.assertEqual(expected, types)
        types = sample_types(self.cursor, 'park')
        expected = [('Park ', 187),
                    ('State park ', 11),
                    ('Dog park ', 10),
                    ('City park ', 5),
                    ('National park ', 3)]
        self.assertEqual(expected, types)

    # Verify features can be sampled
    # Note that the sampling is randomized which dilutes test case
    def test_sample_features(self):
        features_a = sample_features(self.cursor, 'dining')
        features_b = sample_features(self.cursor, 'landmark')
        features_c = sample_features(self.cursor, 'entertainment')
        feature_tests = [features_a, features_b, features_c]
        # List containing lists of tuples
        for group in feature_tests:
            self.assertEqual(5, len(group))
            # List of tuples
            for feat in group:
                # Tuple with 2 places ('feature_name', count)
                for value in feat:
                    self.assertIsNotNone(value)


def main():
    unittest.main(verbosity=3)


main()

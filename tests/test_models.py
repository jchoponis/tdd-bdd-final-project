# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_product(self):
        """It should allow read of a product"""
        product = ProductFactory()
        logger.info("Creating product %s in test_read_product", str(product))
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.available, product.available)
        self.assertEqual(found.category, product.category)

    def test_update_product(self):
        """It should allow updating of a product"""
        product = ProductFactory()
        logger.info("Creating product %s in test_update_product", product.serialize())
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        original_id = product.id
        logger.info("Created product %s in test_update_product", product.serialize())

        new_desc = "a new description!"
        product.description = new_desc
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, new_desc)

        found = Product.all()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, original_id)
        self.assertEqual(found[0].description, new_desc)

    def test_update_product_no_id(self):
        """It should not allow update on product with no id"""
        product = ProductFactory()
        product.create()
        product.id = None
        logger.info("Creating product %s in test_update_product_no_id", product.serialize())
        product.description = "blah blah"
        self.assertRaises(DataValidationError, product.update)

    def test_delete_product(self):
        """It should allow deleting a product"""
        product = ProductFactory()
        product.create()
        logger.info("Created product %s in test_delete_product", product.serialize())

        found = Product.all()
        self.assertEqual(len(found), 1)

        product.delete()

        found_again = Product.all()
        self.assertEqual(len(found_again), 0)

    def test_list_all_products(self):
        """It should allow listing all products"""
        self.assertEqual(len(Product.all()), 0)

        for _ in range(0, 5):
            product = ProductFactory()
            product.create()
            logger.info("Created product %s in test_list_all_products", product.serialize())

        self.assertEqual(len(Product.all()), 5)

    def test_find_product_by_name(self):
        """It should allow find product by name"""
        p_list = []
        for _ in range(0, 5):
            product = ProductFactory()
            product.create()
            logger.info("Created product %s in test_find_product_by_name", product.serialize())
            p_list.append(product)

        logger.info("p_list[0].name is %s", p_list[0].name)
        name1_occurence = len([product for product in p_list if product.name == p_list[0].name])
        found = Product.find_by_name(p_list[0].name)
        found_list = found.all()
        logger.info("list from query obj: %s", found_list)
        self.assertEqual(len(found_list), name1_occurence)
        for fli in found_list:
            self.assertEqual(fli.name, p_list[0].name)

    def test_find_product_by_category(self):
        """It should allow find product by category"""
        p_list = []
        for _ in range(0, 10):
            product = ProductFactory()
            product.create()
            logger.info("Created product %s in test_find_product_by_category", product.serialize())
            p_list.append(product)

        logger.info("p_list[0].category is %s", p_list[0].category)
        occurence = len([product for product in p_list if product.category == p_list[0].category])
        found = Product.find_by_category(p_list[0].category)
        found_list = found.all()
        logger.info("list from query obj: %s", found_list)
        self.assertEqual(len(found_list), occurence)
        for fli in found_list:
            self.assertEqual(fli.category, p_list[0].category)

    def test_find_product_by_price(self):
        """It should allow find product by price"""
        p_list = []
        for _ in range(0, 10):
            product = ProductFactory()
            product.create()
            logger.info("Created product %s in test_find_product_by_price", product.serialize())
            p_list.append(product)

        logger.info("p_list[0].price is %s", p_list[0].price)
        occurence = len([product for product in p_list if product.price == p_list[0].price])
        found = Product.find_by_price(p_list[0].price)
        found_list = found.all()
        logger.info("list from query obj: %s", found_list)
        self.assertEqual(len(found_list), occurence)
        for fli in found_list:
            self.assertEqual(fli.price, p_list[0].price)

        # repeate using string
        found = Product.find_by_price(str(p_list[0].price))
        found_list = found.all()
        self.assertEqual(len(found_list), occurence)
        for fli in found_list:
            self.assertEqual(fli.price, p_list[0].price)

    def test_find_product_by_available(self):
        """It should allow find product by availability"""
        p_list = []
        for _ in range(0, 10):
            product = ProductFactory()
            product.create()
            logger.info("Created product %s in test_find_product_by_available", product.serialize())
            p_list.append(product)

        logger.info("p_list[0].available is %s", p_list[0].available)
        occurence = len([product for product in p_list if product.available == p_list[0].available])
        found = Product.find_by_availability(p_list[0].available)
        found_list = found.all()
        logger.info("list from query obj: %s", found_list)
        self.assertEqual(len(found_list), occurence)
        for fli in found_list:
            self.assertEqual(fli.available, p_list[0].available)

    def test_serialize_product(self):
        """It should allow product serialization"""
        product = ProductFactory()
        product.create()
        logger.info("Created product %s in test_serialize_product", product.serialize())
        result = product.serialize()
        self.assertEqual(product.id, result["id"])
        self.assertEqual(product.name, result["name"])
        self.assertEqual(product.description, result["description"])
        self.assertEqual(product.price, Decimal(result["price"]))
        self.assertEqual(product.available, result["available"])
        self.assertEqual(product.category.name, result["category"])

    def test_deserialize_product(self):
        """It should allow product serialization"""
        product = ProductFactory()
        product.create()
        logger.info("Created product %s in test_deserialize_product", product.serialize())
        serial = product.serialize()
        deserial = product.deserialize(serial)
        self.assertEqual(product.id, deserial.id)
        self.assertEqual(product.name, deserial.name)
        self.assertEqual(product.description, deserial.description)
        self.assertEqual(product.price, Decimal(deserial.price))
        self.assertEqual(product.available, deserial.available)
        self.assertEqual(product.category.name, deserial.category.name)

        serial["available"] = 55
        self.assertRaises(DataValidationError, product.deserialize, serial)

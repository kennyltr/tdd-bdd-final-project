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

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        # Check that it matches the original product
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # update description of product
        test_id = product.id
        product.description = 'testing update function'
        product.update()
        self.assertEqual(product.id, test_id)
        self.assertEqual(product.description, 'testing update function')
        fetchedproduct = Product.all()
        # Check that fetched product displays updated fields
        self.assertEqual(len(fetchedproduct), 1)
        self.assertEqual(fetchedproduct[0].id, test_id)
        self.assertEqual(fetchedproduct[0].description, 'testing update function')
        # test DataValidationError
        product.id = 0
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Verify only 1 product in database
        fetchedproduct = Product.all()
        self.assertEqual(len(fetchedproduct), 1)
        # Remove product from database
        product.delete()
        # Verify no products in database
        fetchedproduct = Product.all()
        self.assertEqual(len(fetchedproduct), 0)

    def test_list_all_products(self):
        """It should list all products"""
        # Verify no products in database
        products = Product.all()
        self.assertEqual(len(products), 0)
        # Create 5 products in database
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        # Fetch all product and assert count is 5
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should find a product by name"""
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        # Retrieve name of first product
        fetchedproducts = Product.all()
        firstproductname = fetchedproducts[0].name
        # Number of occurences of name in list
        count = 0
        for product in fetchedproducts:
            if product.name == firstproductname:
                count += 1
        # Retrieve products with name in database
        fetchedproducts = Product.find_by_name(firstproductname)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(fetchedproducts.count(), count)
        # Assert that each product’s name matches the expected name
        for product in fetchedproducts:
            self.assertEqual(product.name, firstproductname)

    def test_find_product_by_availability(self):
        """It should find a product by availability"""
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        # Retrieve availability of first product
        fetchedproducts = Product.all()
        firstproductavailability = fetchedproducts[0].available
        # Number of occurences of said availability in list
        count = 0
        for product in fetchedproducts:
            if product.available == firstproductavailability:
                count += 1
        # Retrieve products with said availability in database
        fetchedproducts = Product.find_by_availability(firstproductavailability)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(fetchedproducts.count(), count)
        # Assert that each product’s availability matches the expected availability
        for product in fetchedproducts:
            self.assertEqual(product.available, firstproductavailability)

    def test_find_product_by_category(self):
        """It should find a product by category"""
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        # Retrieve category of first product
        fetchedproducts = Product.all()
        firstproductcategory = fetchedproducts[0].category
        # Number of occurences of said category in list
        count = 0
        for product in fetchedproducts:
            if product.category == firstproductcategory:
                count += 1
        # Retrieve products with said category in database
        fetchedproducts = Product.find_by_category(firstproductcategory)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(fetchedproducts.count(), count)
        # Assert that each product’s category matches the expected category
        for product in fetchedproducts:
            self.assertEqual(product.category, firstproductcategory)

    def test_find_product_by_price(self):
        """It should find a product by price"""
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        # Retrieve price of first product
        fetchedproducts = Product.all()
        firstproductprice = fetchedproducts[0].price
        # Number of occurences of said price in list
        count = 0
        for product in fetchedproducts:
            if product.price == firstproductprice:
                count += 1
        # Retrieve products with said price in database
        fetchedproducts = Product.find_by_price(firstproductprice)
        # Assert if the count of the found products matches the expected count.
        self.assertEqual(fetchedproducts.count(), count)
        # Assert that each product’s price matches the expected price
        for product in fetchedproducts:
            self.assertEqual(product.price, firstproductprice)
        strprice = str(firstproductprice) + ' '
        fetchedproduct = Product.find_by_price(strprice)
        self.assertEqual(fetchedproduct[0].price, firstproductprice)

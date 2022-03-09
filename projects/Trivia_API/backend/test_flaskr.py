import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from config import *

class Trivia_Testing(unittest.TestCase):
    #Trivia test class

    def setUp(self):
    #Initialize test.
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = 'postgresql://{}/{}'.format(
            'postgres:LMAO@127.0.0.1:5433', self.database_name)
        setup_db(self.app, self.database_path)
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
      res = self.client().get('/questions?page=1')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['current_category'], None)
      self.assertTrue(len(data['questions']))
      self.assertTrue(data['total_questions'])
      self.assertTrue(data['categories'])
      
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_get_questions(self):
      res = self.client().get('/questions?page=100')

      self.assertEqual(res.status_code, 404)

    def test_get_questions_by_category(self):
      res = self.client().get('/questions?page=1&category_id=1')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['current_category'], 1)
      self.assertTrue(len(data['questions']))
      self.assertTrue(data['total_questions'])
      self.assertTrue(data['categories'])

    def test_404_get_questions_by_category(self):
      res = self.client().get('/questions?page=1&category_id=100')

      self.assertEqual(res.status_code, 404)

    def test_get_questions_by_search_term(self):
      res = self.client().get('/questions?page=1&search_term=movie')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['current_category'], None)
      self.assertTrue(len(data['questions']))
      self.assertTrue(data['total_questions'])
      self.assertTrue(data['categories'])

    def test_delete_questions(self):
      res = self.client().delete('/questions/20')

      self.assertEqual(res.status_code, 200)

    def test_422_delete_questions(self):
      res = self.client().delete('/questions/1000')

      self.assertEqual(res.status_code, 422)

    def test_create_questions(self):
      new_question = {
        'question': 'new question',
        'answer': 'new answer',
        'category': 1,
        'difficulty': 1,
      }
      res = self.client().post('/questions', json=new_question)
      self.assertEqual(res.status_code, 201)

    def test_500_create_questions(self):
      invalid_question = {
        'question': 'invalid question',
        'answer': 'invalid answer',
        'category': 'Not integer',
        'difficulty': 'Not integer',
      }
      res = self.client().post('/questions', json=invalid_question)

      self.assertEqual(res.status_code, 500)

    def test_get_categories(self):
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(len(data['categories']))

    def test_quizzes(self):
      body = {
        'previous_questions': [ 2, 4 ],
        'category_id': 5,
      }
      res = self.client().post('/quizzes', json=body)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

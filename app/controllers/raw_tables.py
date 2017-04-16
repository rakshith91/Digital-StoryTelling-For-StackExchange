import sys
import csv
import json

from flask import Blueprint
from flask.views import MethodView
from flask import jsonify
from flask import abort
from flask_sqlalchemy_session import current_session as session

from sqlalchemy import func, desc

from models.data import Location, Tags, Users, Questions, Answers, ViewSkillsLocations, ViewAnswersLocalTime
from core import format_attrs, Paginator, QueryFilter

raw_tables_handler = Blueprint('raw_tables_handler', __name__)


class RawTableController(MethodView):
	def get(self, id=None):
		if id is None:
			base_query = self.select(session)
			filtered_query = self.filter(base_query)
			grouped_query = self.group(filtered_query)
			ordered_query = self.order(grouped_query)
			paginated_query = self.paginate(ordered_query)
			objects = paginated_query

			self.row_count = ordered_query.count();

			args = zip(self.input_fields, self.output_fields)
			kwargs = {
				"preprocessors": getattr(self, "preprocessors", {}),
				"postprocessors": getattr(self, "postprocessors",[]),
			}
			response = format_attrs(objects, *args, **kwargs)

			response = self.postprocess(response)

			return jsonify(**response)
		else:
			obj = session.query(self.table).get(int(id))
			if obj is not None:
				return jsonify(**{x: getattr(obj, x) for x in self.input_fields})
			else:
				abort(404)

	def select(self, obj):
		columns = [getattr(self.table, x).label(x) for x in self.input_fields]
		return obj.query(*columns)

	def filter(self, query):
		self.query_filter = QueryFilter(query)
		return self.query_filter.filter()

	def group(self, x):
		return x

	def order(self, x):
		return x

	def paginate(self, query, page_size=10):
		self.paginator = Paginator(page_size)
		return self.paginator.paginate(query)

	def postprocess(self, response):
		if hasattr(self, 'query_filter'):
			response['filter'] = self.query_filter.filter_data()
		else:
			response['filter'] = []

		response["row_count"] = self.row_count
		response["page_size"] = self.paginator.page_size
		response["table"] = True
		return response


class UsersController(RawTableController):
	table = Users
	input_fields = ['id', 'name', 'reputation', 'location_id', 'views', 'upvotes',
						'downvotes', 'age']
	output_fields = ['ID', 'Name', 'Reputation', 'Location ID', 'Views', 'Upvotes',
						'Downvotes', 'Age']
	postprocessors = {
		"location_id": {
			"type": "link_replace",
			"url": "/locations/{{location_id}}/",
			"replace": "{{id}} ({{city}}, {{state}}, {{country}})",
		},
		"name": {
			"type": "link_open",
			"url": "//stackoverflow.com/users/{{id}}",
		}
	}

class LocationController(RawTableController):
	table = Location
	input_fields = ['id', 'location', 'city', 'state', 'country', 'timezone']
	output_fields = ['ID', 'Location', 'City', 'State', 'Country', 'Timezone']
	postprocessors = {
		"city": {
			"type": "link_open",
			"url": "//maps.google.com/maps/place/{{city}},{{state}},{{country}}",
		},
		"state": {
			"type": "link_open",
			"url": "//maps.google.com/maps/place/{{state}},{{country}}",
		},
		"country": {
			"type": "link_open",
			"url": "//maps.google.com/maps/place/{{country}}",
		}
	}
	location = "{{city}}, {{state}}, {{country}}"
	score = "1"

	def postprocess(self, response):
		response = super(LocationController, self).postprocess(response)

		response['location'] = self.location
		response['score'] = self.score

		return response

class TagsController(RawTableController):
	table = Tags
	input_fields = ['id', 'name']
	output_fields = ['ID', 'Name']
	postprocessors = {
		"name": {
			"type": "link_open",
			"url": "//stackoverflow.com/questions/tagged/{{name}}",
		},
	}
class QuestionsController(RawTableController):
	table = Questions
	input_fields = ['id', 'title', 'accepted_answer_id', 'score', 'author_id',
					'answer_count']
	output_fields = ['ID', 'Title', 'Accepted Answer ID', 'Score', 'Author ID',
					'Answer Count']
	postprocessors = {
		"id": {
			"type": "link_open",
			"url": "//stackoverflow.com/questions/{{id}}",
		},
		"accepted_answer_id": {
			"type": "link_open",
			"url": "//stackoverflow.com/a/{{accepted_answer_id}}",
		},
		"author_id": {
			"type": "link_open",
			"url": "//stackoverflow.com/users/{{author_id}}",
		}
	}

class AnswersController(RawTableController):
	table = Answers
	input_fields = ['id', 'question_id', 'score', 'author_id']
	output_fields = ['ID', 'Question ID', 'Score', 'Author ID']
	postprocessors = {
		"author_id": {
			"type": "link_open",
			"url": "//stackoverflow.com/users/{{author_id}}",
		},
		"question_id": {
			"type": "link_replace",
			"url": "/questions/{{question_id}}/",
			"replace": "{{title}}",
		},
		"id": {
			"type": "link_open",
			"url": "//stackoverflow.com/a/{{id}}",
		},
	}


class ViewSkillsLocationsController(RawTableController):
	table = ViewSkillsLocations
	input_fields = ['city', 'country', 'state', 'skill_id', 'total_score']
	output_fields = ['City', 'Country', 'State', 'Skill ID', 'Total Score']
	location = "{{city}}, {{state}}, {{country}}"
	score = "{{total_score}}"

	def order(self, obj):
		return obj.order_by(desc(ViewSkillsLocations.total_score))

	def postprocess(self, response):
		response = super(ViewSkillsLocationsController, self).postprocess(response)

		response['location'] = self.location
		response['score'] = self.score

		return response



class ViewAnswersLocalTimeController(RawTableController):
	table = ViewAnswersLocalTime
	input_fields = ["activity", "hour"]
	output_fields = ["Activity", "Hour"]

	activity = func.count(ViewAnswersLocalTime.id).label("activity")
	hour_part = func.date_part('hour', ViewAnswersLocalTime.local_creation_date).label("hour")

	def select(self, obj):
		return obj.query(self.activity, self.hour_part)

	def group(self, obj):
		return obj.group_by(self.hour_part)

	def order(self, obj):
		return obj.order_by(desc(self.activity))

	def filter(self, query):
		filtered = super(ViewAnswersLocalTimeController, self).filter(query)
		return filtered.filter(ViewAnswersLocalTime.local_creation_date != None)

	def paginate(self, query):
		return super(ViewAnswersLocalTimeController, self).paginate(query, 24)

	def postprocess(self, response):
		response = super(ViewAnswersLocalTimeController, self).postprocess(response)
		response["timechart"] = True
		return response

raw_tables_handler.add_url_rule( '/users/<int:id>/',
	view_func=UsersController.as_view('users_id'))
raw_tables_handler.add_url_rule( '/users/',
	view_func=UsersController.as_view('users'))

raw_tables_handler.add_url_rule( '/locations/<int:id>/',
	view_func=LocationController.as_view('locations_id'))
raw_tables_handler.add_url_rule( '/locations/',
	view_func=LocationController.as_view('locations'))

raw_tables_handler.add_url_rule( '/questions/<int:id>/',
	view_func=QuestionsController.as_view('questions_id'))
raw_tables_handler.add_url_rule( '/questions/',
	view_func=QuestionsController.as_view('questions'))

raw_tables_handler.add_url_rule( '/answers/<int:id>/',
	view_func=AnswersController.as_view('answers_id'))
raw_tables_handler.add_url_rule( '/answers/',
	view_func=AnswersController.as_view('answers'))

raw_tables_handler.add_url_rule( '/tags/<int:id>/',
	view_func=TagsController.as_view('tags_id'))
raw_tables_handler.add_url_rule( '/tags/',
	view_func=TagsController.as_view('tags'))

raw_tables_handler.add_url_rule( '/view_skills_locations/',
	view_func=ViewSkillsLocationsController.as_view('view_skills_locations'))

raw_tables_handler.add_url_rule( '/view_answers_local_time/',
	view_func=ViewAnswersLocalTimeController.as_view('view_answers_local_time'))

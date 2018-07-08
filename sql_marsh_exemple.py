import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, pre_load , post_load

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quotes.db'
db = SQLAlchemy(app)

##### MODELS #####

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(80))
    last = db.Column(db.String(80))
    def __repr__(self):
        return "first: {} ,last:{}".format(self.first ,self.last)

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship(
        'Author',
        backref=db.backref('quotes', lazy='dynamic'),
    )
    posted_at = db.Column(db.DateTime)

##### SCHEMAS #####

class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    first = fields.Str(required=True)
    last = fields.Str(required=True)
    formatted_name = fields.Method('format_name', dump_only=True)

    def format_name(self, author):
        return '{}, {}'.format(author.last, author.first)
    @post_load
    def make_author(self , data):
        return Author(**data)



# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class QuoteSchema(Schema):
    id = fields.Int(dump_only=True)
    author = fields.Nested(AuthorSchema, validate=must_not_be_blank)
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)
  

author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)
quote_schema = QuoteSchema()
quotes_schema = QuoteSchema(many=True, only=('id', 'content'))

##### API #####
@app.route('/author', methods=['POST'])
def new_user():
    json_data = request.get_json(force=True)
    if not json_data :
        return jsonify({'message': "invalide json format" }), 400
    data , errors   = author_schema.load(json_data)
    if errors:
        return jsonify({"errors" : errors }) , 422
    else :
        first, last = data.first, data.last #first, last = "chih", "smail"
        author = Author(first=first, last=last)
        db.session.add(author)
        db.session.commit()
        result = authors_schema.dump(Author.query.all())
        return jsonify({'message': 'Created new quote.','authors': result})

@app.route('/authors')
def get_authors():
    authors = Author.query.all()
    result = authors_schema.dump(authors)
    return jsonify({'authors': result})

@app.route('/authors/<int:pk>')
def get_author(pk):
    try:
        author = Author.query.get(pk)
    except IntegrityError:
        return jsonify({'message': 'Author could not be found.'}), 400
    author_result = author_schema.dump(author)
    quotes_result = quotes_schema.dump(author.quotes.all())
    return jsonify({'author': author_result, 'quotes': quotes_result})

@app.route('/quotes/', methods=['GET'])
def get_quotes():
    quotes = Quote.query.all()
    result = quotes_schema.dump(quotes)
    return jsonify({'quotes': result})

@app.route('/quotes/<int:pk>')
def get_quote(pk):
    try:
        quote = Quote.query.get(pk)
    except IntegrityError:
        return jsonify({'message': 'Quote could not be found.'}), 400
    result = quote_schema.dump(quote)
    return jsonify({'quote': result})

@app.route('/quotes/', methods=['POST'])
def new_quote():
    json_data = request.get_json(force=True)
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data ,errors= quote_schema.load(json_data)
    if errors:
        return jsonify({"errors" : errors }) , 422
    else :
        data ,errors= quote_schema.dump(data)
        first, last = data['author']['first'], data['author']['last']
        author = Author.query.filter_by(first=first, last=last).first()
        if author is None:
            # Create a new author
            author = Author(first=first, last=last)
            db.session.add(author)
            # Create new quote
            quote = Quote(
                content=data['content'],
                author=author,
                posted_at=datetime.datetime.utcnow()
                )
            db.session.add(quote)
            db.session.commit()
            result = quote_schema.dump(Quote.query.get(quote.id))
            return jsonify({'message': 'Created new quote.','quote': result})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=5000)


from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'author': self.author}


with app.app_context():
    db.create_all()
    if not Book.query.first():
        initial_books = [
            Book(title='1984', author='George Orwell'),
            Book(title='The Great Gatsby', author='F. Scott Fitzgerald'),
            Book(title='To Kill a Mockingbird', author='Harper Lee'),
        ]
        db.session.add_all(initial_books)
        db.session.commit()

# Rotas
@app.route('/books', methods=['GET'])
def get_books():
    return jsonify([book.to_dict() for book in Book.query.all()]), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description='Book not found')
    return jsonify(book.to_dict()), 200

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'author')):
        abort(400, description="Missing fields: 'title' or 'author'")
    new_book = Book(title=data['title'], author=data['author'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created', 'book': new_book.to_dict()}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description='Book not found')
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    db.session.commit()
    return jsonify({'message': 'Book updated', 'book': book.to_dict()}), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404, description='Book not found')
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)

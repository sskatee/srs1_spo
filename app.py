from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

books = []
next_id = 1

GENRES = ["Фантастика", "Детектив", "Роман", "Научпоп", "Фэнтези", "Биография"]


def find_book(book_id):
    for b in books:
        if b["id"] == book_id:
            return b
    return None


@app.route("/")
def index():
    total = len(books)
    avg_rating = round(sum(b["rating"] for b in books) / total, 2) if total else 0
    return render_template(
        "index.html",
        total=total,
        avg_rating=avg_rating,
        last_books=books[-3:][::-1],
    )


@app.route("/books")
def books_list():
    genre = request.args.get("genre", "")
    min_rating = request.args.get("min_rating", "")

    filtered = books

    if genre:
        filtered = [b for b in filtered if b["genre"] == genre]

    if min_rating:
        try:
            threshold = float(min_rating)
            filtered = [b for b in filtered if b["rating"] >= threshold]
        except ValueError:
            pass

    filtered = sorted(filtered, key=lambda b: b["rating"], reverse=True)

    return render_template(
        "books.html",
        books=filtered,
        genres=GENRES,
        selected_genre=genre,
        min_rating=min_rating,
    )


@app.route("/add", methods=["GET", "POST"])
def add_book():
    errors = {}

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        genre = request.form.get("genre", "").strip()
        rating_raw = request.form.get("rating", "").strip()
        review = request.form.get("review", "").strip()

        if not title:
            errors["title"] = "Название обязательно."
        elif len(title) > 100:
            errors["title"] = "Название не длиннее 100 символов."

        if not author:
            errors["author"] = "Автор обязателен."

        if genre not in GENRES:
            errors["genre"] = "Выберите жанр из списка."

        try:
            rating = float(rating_raw)
            if not (1 <= rating <= 5):
                errors["rating"] = "Оценка должна быть от 1 до 5."
        except ValueError:
            rating = 0
            errors["rating"] = "Оценка должна быть числом."

        if not errors:
            global next_id
            book = {
                "id": next_id,
                "title": title,
                "author": author,
                "genre": genre,
                "rating": rating,
                "review": review,
            }
            books.append(book)
            next_id += 1
            return redirect(url_for("book_detail", book_id=book["id"]))

        return render_template(
            "add_book.html",
            errors=errors,
            genres=GENRES,
            form_data={
                "title": title,
                "author": author,
                "genre": genre,
                "rating": rating_raw,
                "review": review,
            },
        )

    return render_template("add_book.html", errors={}, genres=GENRES, form_data={})


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = find_book(book_id)
    if book is None:
        abort(404)
    return render_template("book_detail.html", book=book)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        abort(404)
    books.remove(book)
    return redirect(url_for("books_list"))


if __name__ == "__main__":
    books.extend([
        {"id": 1, "title": "Война и Мир", "author": "Лев Толстой",
         "genre": "Роман", "rating": 5, "review": "Бесспорная классика русскрй литературы!"},
        {"id": 2, "title": "Убийство в Восточном экспрессе", "author": "Агата Кристи",
         "genre": "Детектив", "rating": 4, "review": " Местами непонятно, но в целом интересно"},
        {"id": 3, "title": "Великий Гэтсби", "author": "Фрэнсис Скотт Фитцджеральд",
         "genre": "Роман", "rating": 5, "review": "Стоит прочитать каждому!"},
    ])
    next_id = 4

    app.run(debug=True)
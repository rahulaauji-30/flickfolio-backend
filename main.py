from flask import Flask, request, jsonify,render_template
import os
import shutil
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import current_user
from flask_cors import CORS
app = Flask(__name__)
CORS(app=app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost/movie"
db = SQLAlchemy(app)


# Database models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    photo = db.Column(db.String(1000), nullable=True)


class Favourites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)


@app.route("/")
def home():
    return render_template("index.html")

# TODO 1 : Register User
@app.route("/register/user", methods=["POST"])
def register_user():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    try:
        new_user = Users(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Users registered successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Users with this email already exists"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to register user", "error": str(e)}), 500


#TODO 2 : Get Registered User
@app.route("/get/user/<int:id>", methods=["GET"])
def get_user(id):
    user = Users.query.get(id)
    if user:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "photo": user.photo
        }
        return jsonify(user_data), 200
    else:
        return jsonify({"message": f"Users Not found with user id {id}"}), 404

#TODO:Final
@app.route("/check-user/<string:email>",methods=["GET"])
def check_user(email):
    user = Users.query.filter_by(email=email).first()
    if user:
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "photo": user.photo
        }), 200
    else:
        return jsonify({"message": "Email not found in database"}), 404

# TODO:3 Saving favourite movies
@app.route("/add-to-favourite/<int:user_id>/<int:movieid>", methods=["POST"])
def add_favourite(user_id, movieid):
    # Create a new favourite entry
    new_favourite = Favourites(user_id=user_id, movie_id=movieid)

    # Add the new favourite to the session
    db.session.add(new_favourite)

    try:
        # Commit the session to save the changes to the database
        db.session.commit()
        response = {
            "message": "Movie added to favourites"
        }
        return jsonify(response), 200
    except Exception as e:
        # Rollback the session in case of any error
        db.session.rollback()
        response = {
            "message": "Failed to add movie to favourites",
            "error": str(e)
        }
        return jsonify(response), 500


# TODO:4 Saving Watch list
@app.route("/add-to-watchlist/<int:user_id>/<int:movieid>", methods=["POST"])
def add_watchlist(user_id, movieid):
    # Create a new watchlist entry
    new_watchlist = Watchlist(user_id=user_id, movie_id=movieid)

    # Add the new watchlist entry to the session
    db.session.add(new_watchlist)

    try:
        # Commit the session to save the changes to the database
        db.session.commit()
        response = {
            "message": "Movie added to watch list"
        }
        return jsonify(response), 200
    except Exception as e:
        # Rollback the session in case of any error
        db.session.rollback()
        response = {
            "message": "Failed to add movie to watch list",
            "error": str(e)
        }
        return jsonify(response), 500


# TODO 5 :Get favourites
@app.route("/get-favourites/<int:user_id>", methods=["GET"])
def get_favourites(user_id):
    # Query the favourites for the given user ID
    favourites = Favourites.query.filter_by(user_id=user_id).all()

    if favourites:
        # If favourites are found, prepare the response
        favourite_movies = [{"movie_id": favourite.movie_id} for favourite in favourites]
        response = {
            "user_id": user_id,
            "favourite_movies": favourite_movies
        }
        return jsonify(response), 200
    else:
        # If no favourites are found, return a message
        return jsonify({"message": "No favourites found for the user"}), 404


# TODO 6: Get watchlist of a user
@app.route("/get-watchlist/<int:user_id>", methods=["GET"])
def get_watchlist(user_id):
    # Query the watchlist for the given user ID
    watchlist = Watchlist.query.filter_by(user_id=user_id).all()

    if watchlist:
        # If watchlist is found, prepare the response
        watchlist_movies = [{"movie_id": item.movie_id} for item in watchlist]
        response = {
            "user_id": user_id,
            "watchlist_movies": watchlist_movies
        }
        return jsonify(response), 200
    else:
        # If no watchlist is found, return a message
        return jsonify({"message": "No watchlist found for the user"}), 404


# TODO 7 : Remove from favourite route
@app.route("/remove-from-favourite/<int:user_id>/<int:movieid>", methods=["POST"])
def remove_favourite(user_id, movieid):
    favourite_to_delete = Favourites.query.filter_by(user_id=user_id, movie_id=movieid).first()
    if favourite_to_delete:
        db.session.delete(favourite_to_delete)
        try:
            db.session.commit()
            return jsonify({"message": "Movie removed from favourites"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to remove movie from favourites", "error": str(e)}), 500
    else:
        return jsonify({"message": "Movie not found in favourites", "error": "No such favourite exists"}), 404


# TODO 8: Remove from watchlist route
@app.route("/remove-from-watchlist/<int:user_id>/<int:movieid>", methods=["POST"])
def remove_watchlist(user_id, movieid):
    watchlist_to_delete = Watchlist.query.filter_by(user_id=user_id, movie_id=movieid).first()
    if watchlist_to_delete:
        db.session.delete(watchlist_to_delete)
        try:
            db.session.commit()
            return jsonify({"message": "Movie removed from watchlist"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to remove movie from watchlist", "error": str(e)}), 500
    else:
        return jsonify({"message": "Movie not found in watchlist", "error": "No such watchlist entry exists"}), 404


# TODO 9: Upload profile picture route
@app.route("/upload-profile-pic/<int:id>", methods=["POST"])
def upload_profile_pic(id):
    file = request.files.get("image")
    if file:
        if not os.path.exists("profile-pictures"):
            os.makedirs("profile-pictures")
        user_folder = os.path.join("profile-pictures", str(id))
        try:
            if os.path.exists(user_folder):
                shutil.rmtree(user_folder)
            os.makedirs(user_folder)
            file.save(os.path.join(user_folder, file.filename))

            # Update the user's photo path in the database
            user = Users.query.get(id)
            if user:
                user.photo = os.path.join(user_folder, file.filename)
                db.session.commit()

            return "File Saved Successfully", 200
        except Exception as e:
            return jsonify({"message": "Failed to upload profile picture", "error": str(e)}), 500
    else:
        return jsonify({"message": "File is not selected"}), 400


# TODO 10: Remove profile picture route
@app.route("/remove-profile-pic/<int:id>", methods=["POST"])
def remove_profile_pic(id):
    user_folder = os.path.join("profile-pictures", str(id))
    try:
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)

            # Remove the photo path from the user's database record
            user = Users.query.get(id)
            if user:
                user.photo = None
                db.session.commit()

            return 'Profile picture removed successfully', 200
        else:
            return 'Profile picture does not exist', 404
    except Exception as e:
        return jsonify({"message": "Failed to remove profile picture", "error": str(e)}), 500

# Get all users
@app.route("/get/all-users", methods=["GET"])
def get_all_users():
    users = Users.query.all()
    all_users = [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "photo": user.photo
    } for user in users]
    
    return jsonify(all_users), 200


if __name__ == "__main__":
    app.run()

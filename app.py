"""Flask Application for Paws Rescue Center."""
from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm, EditDishForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///themealplanner.db"
app.config["SECRET_KEY"] = "dfewfew123213rwdsgert34tgfd1234trgf"

# init db
db = SQLAlchemy(app)

"""Model for Dishes."""


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    ingredients = db.Column(db.String)
    diet = db.Column(db.String)
    instructions = db.Column(db.String)
    posted_by = db.Column(db.String, db.ForeignKey("user.id"))


"""Model for Users."""


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    dishes = db.relationship("Dish", backref="user")


db.create_all()

# Create "team" user and add it to session
team = User(
    full_name="Healthy Diet Team", email="team@healthydiet.co", password="adminpass"
)

db.session.add(team)

# Create all dishes
branzino = Dish(
    name="Mediterranean Grilled Branzino",
    diet="Pescatarians",
    ingredients="Branzinos, olive oil, shallots, garlic, parsley, dill, salt, Aleppo pepper, and lemons",
    instructions="""Cut 3 slits on the branzino using a sharp knife, you don't need to cut all the way through.
    
    In a medium sized bowl mix the olive oil with shallots, mince garlic, parsley, dill, Aleppo pepper, salt and lemon juice. Spoon half this mixture inside the branzinos. Place the lemon slices in the cavity of the branzinos and seal it using a couple of toothpicks. Place the branzinos on a baking sheet and spoon the rest of the lemon herb mixture on top.
    
    While the fish is being marinated, prepare the grill to high. You can use charcoal or gas grill. Rub half of a potato on the grates to avoid the fish sticking.
    
    Place the branzinos on the grates and grill for about 8 minutes on each side. Flip only once. It's okay if the skin sticks to the grates. Grill the branzino until the skin is brown and crispy and the fish is cooked completely.
    
    Make the tomato herb relish. In a medium sized bowl mix the tomatoes with the jalapeno, cilantro, parsley, red onion, lemon juice, olive oil, salt, pepper and sumac.
    
    Place the grilled branzino on the platter and top with the tomato herb relish. Serve immediately.""",
)
octopus = Dish(
    name="Grilled Octopus",
    diet="Pescatarians",
    ingredients="octopus, potato, parsley, garlic, olive oil",
    instructions="""In a large pot, bring 8 quarts of water to a boil. Add the salt, peppercorns, bay leaf and the penny. Holding the octopus by the head, carefully and quickly dip the tentacles into the water 3 times, then lower it into the pot. Reduce the heat to moderately low and simmer until almost tender, about 1 hour and 15 minutes. If necessary, place a plate over the octopus to keep it submerged.

    Add the potatoes and cook until the octopus and potatoes are tender, about 25 minutes more. Transfer the octopus and potatoes to a work surface; discard the braising liquid. Separate the tentacles and cut the head in half. Using a paper towel, wipe the purple skin off the tentacles, leaving the suckers intact. Thinly slice the potatoes and arrange on a platter.

    Light a grill or preheat a grill pan. Brush the octopus with the 3 tablespoons of olive oil. Grill over moderately high heat, turning, until lightly charred, about 4 minutes. Arrange the octopus on the platter with the potatoes. Drizzle with the lemon juice and more olive oil. Sprinkle with the paprika, flaky sea salt and parsley leaves; serve.

    """,
)
lamb = Dish(
    name="Lamb Chop",
    diet="Paleo",
    ingredients="lamb chop, onion, apple, salt, honey",
    instructions="""Heat a cast iron or non-stick heavy bottom skillet over medium to medium-high heat. 

    Melt 2 Tbsp. butter in the pan and sear the lamb chops in 2 batches for 2 minutes per side. 

    Add the herbs and garlic, lower the heat to medium, then baste the chops with herbs and garlic butter. 

    Use a spoon to pour the juices over the chops while the pan is tilted away from you. Do not burn the butter or drippings. 

    Remove the chops to rest and add the onions and apples to the pan, then sauté for 6-8 minutes until the apples are tender and translucent and the onions begin to caramelize. 

    Serve the lamb with the apples and onions alongside a green salad or couscous.
    """,
)
shrimp = Dish(
    name="Shimp Taco",
    diet="Pescatarians",
    ingredients="shrimp, cilantro, lime, salt, olive oil, avocado, onion, tortilla",
    instructions="""In a large bowl, whisk together lime juice, cilantro, garlic, cumin, olive oil, lime zest and season with salt. Add shrimp and cover with plastic wrap. Let marinate 20 minutes in refrigerator. 

Make slaw: in a large bowl combine all slaw ingredients. Toss gently to combine and season with salt. 

Make garlic-lime mayo: in a medium bowl, combine all ingredients. Whisk and season with salt. 

Preheat grill or grill pan to medium heat. Grill shrimp until pink and opaque, about 2 to 3 minutes per side. 

Build tacos: add a scoop of slaw, a few shrimp, and a drizzle of the garlic-lime mayo to each taco. Garnish with cilantro and serve.
""",
)

# Add all dishes to the session
db.session.add(branzino)
db.session.add(octopus)
db.session.add(lamb)
db.session.add(shrimp)

# Commit changes in the session
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
finally:
    db.session.close()


@app.route("/")
def homepage():
    """View function for Home Page."""
    dishes = db.session.query(Dish).all()
    return render_template("home.html", dishes=dishes)


@app.route("/about")
def about():
    """View function for About Page."""
    return render_template("about.html")


@app.route("/details/<int:dish_id>", methods=["POST", "GET"])
def dish_details(dish_id):
    """View function for Showing Details of Each Dish."""
    form = EditDishForm()
    dish = db.session.query(Dish).get(dish_id)
    if dish is None:
        abort(404, description="No Dish was Found with the given ID")
    if form.validate_on_submit():
        dish.name = form.name.data
        dish.ingredients = form.ingredients.data
        dish.diet = form.diet.data
        dish.instructions = form.instructions.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template(
                "details.html",
                dish=dish,
                form=form,
                message="A Dish with this name already exists!",
            )
        finally:
            db.session.close()
    return render_template("details.html", dish=dish, form=form)


@app.route("/delete_dish/<int:dish_id>")
def delete_dish(dish_id):
    """View function for Deleting Dishes."""
    dish = Dish.query.get(dish_id)
    if dish is None:
        abort(404, description="No Dish was Found with the given ID")
    db.session.delete(dish)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for("homepage"))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    """View function for New User Sign Up."""
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template(
                "signup.html",
                form=form,
                message="This Email already exists in the system! Please Login instead.",
            )
        return render_template("signup.html", message="Successfully signed up")
    return render_template("signup.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    """View function for User Login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data, password=form.password.data
        ).first()
        if user is None:
            return render_template(
                "login.html", form=form, message="Wrong Credentials. Please Try Again."
            )
        else:
            session["user"] = user.id
            return render_template("login.html", message="Successfully Logged In!")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """View function for User Logout."""
    if "user" in session:
        session.pop("user")
    return redirect(url_for("homepage"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8888)

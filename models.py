from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.associationproxy import association_proxy

# pass subclass of DeclarativeBase
class Base(DeclarativeBase):
    pass

# create the db object
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

## Associative tables (for many-to-many relationships)

# `polishes` to `order_logs`
polishes_order_logs = db.Table(
    "polishes_order_logs",
    db.Column("polish_id", db.Integer, db.ForeignKey("polishes.id"), primary_key=True),
    db.Column(
        "order_log_id", db.Integer, db.ForeignKey("order_logs.id"), primary_key=True
    ),
)

# `polishes` to `mani_photos`
polishes_mani_photos = db.Table(
    "polishes_mani_photos",
    db.Column("polish_id", db.Integer, db.ForeignKey("polishes.id"), primary_key=True),
    db.Column(
        "mani_photo_id", db.Integer, db.ForeignKey("mani_photos.id"), primary_key=True
    ),
)

# `polishes` to `mani_logs`
# polishes_mani_logs = db.Table(
#    "polishes_mani_logs",
#    db.Column("polish_id", db.Integer, db.ForeignKey("polishes.id"), primary_key=True),
#    db.Column(
#        "mani_log_id", db.Integer, db.ForeignKey("mani_logs.id"), primary_key=True
#    ),
#)
class PolishManiLog(db.Model):
	__tablename__ = "polishes_mani_logs"
	
	polish_id = db.Column(db.Integer, db.ForeignKey("polishes.id"), primary_key=True)
	mani_log_id = db.Column(db.Integer, db.ForeignKey("mani_logs.id"), primary_key=True)
	
	n_fingers = db.Column(db.Integer) # number of fingers the polish was used on
	n_coats = db.Column(db.Integer) # number of coats used
	
	polish = relationship("Polish", back_populates="mani_associations")
	mani_log = relationship("ManiLog", back_populates="polish_associations")

class SimilarTo(db.Model):
    __tablename__ = "similar_to"

    polish_1_id = db.Column(
        db.Integer,
        db.ForeignKey("polishes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    polish_2_id = db.Column(
        db.Integer,
        db.ForeignKey("polishes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # rank = db.Column(db.Integer, nullable=True) # to implement later: ranking of similarity structure

    __table_args__ = (
        db.CheckConstraint("polish_1_id <> polish_2_id", name="ck_similar_not_self"),
        db.CheckConstraint(
            "polish_1_id < polish_2_id", name="ck_similar_canonical_order"
        ),
    )

    polish_1 = relationship(
        "Polish", foreign_keys=[polish_1_id], back_populates="similarity_links_1"
    )
    polish_2 = relationship(
        "Polish", foreign_keys=[polish_2_id], back_populates="similarity_links_2"
    )

# `polishes` to `tags`
polishes_tags = db.Table(
    "polishes_tags",
    db.Column("polish_id", db.Integer, db.ForeignKey("polishes.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)

# `mani_logs` to `tags`
mani_logs_tags = db.Table(
    "mani_logs_tags",
    db.Column("mani_log_id", db.Integer, db.ForeignKey("mani_logs.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)

# `ingredients` to `order_logs`
ingredients_order_logs = db.Table(
    "ingredients_order_logs",
    db.Column(
        "ingredient_id", db.Integer, db.ForeignKey("ingredients.id"), primary_key=True
    ),
    db.Column(
        "order_log_id", db.Integer, db.ForeignKey("order_logs.id"), primary_key=True
    ),
)

# `ingredients` to `recipes`
ingredients_recipes = db.Table(
    "ingredients_recipes",
    db.Column(
        "ingredient_id", db.Integer, db.ForeignKey("ingredients.id"), primary_key=True
    ),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
)

## Main tables

# class: Brand
# creates `brands` table
class Brand(db.Model):
    __tablename__ = "brands"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    name = db.Column(db.String(75), nullable=False, unique=True)
    type = db.Column(
        db.Enum(
            "indie",
            "boutique",
            "mainstream",
            "luxury",
            "unknown",
            name="brand_types",
            nullable=False,
            default="unknown",
        )
    )
    website_url = db.Column(db.String(255))  # optional field for later
    abbrev = db.Column(db.String(20), nullable=True)

    # Relationships
    # Brand to polish: one-to-many (parent)
    polish = relationship("Polish", back_populates="brand")


# class: Recipe
# creates `recipes` table
class Recipe(db.Model):
    __tablename__ = "recipes"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    name = db.Column(db.String(150), nullable=False)
    # eventually add:
    # ingredients
    # qty (of each ingredient)
    # notes

    # Relationships
    # recipes to polishes: one-to-one (parent)
    polish = relationship("Polish", back_populates="recipe", uselist=False)
    # recipes to ingredients: many-to-many
    ingredient = relationship(
        "Ingredient",
        secondary=ingredients_recipes,
        back_populates="recipe",
        lazy="dynamic",
    )


# class: Polish
# creates `polishes` table
class Polish(db.Model):
    __tablename__ = "polishes"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    name = db.Column(db.String(150), nullable=False)
    polish_type = db.Column(
        db.Enum(
            "color", "top coat", "base coat", "stamping polish", "other",
            name="polish_types",
        ),
        nullable=True,
    )
    color_family = db.Column(
        db.Enum(
            "clear/white", "black", "grey/silver", "nude/gold/brown",
            "red","coral/orange","yellow","green","teal/turq/aqua",
            "blue","indigo","violet","fuchsia","pink","base/top coat",
            name="color_family_types",
        ),
        nullable=True
    )
    full_desc = db.Column(db.String(400))
    destashed_flag = db.Column(db.Boolean, default=False, nullable=False)

    # Foreign keys (to linked parent tables)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id"),
        unique=True,
        nullable=True,
    )
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)

    # Relationships
    # Recipes to polishes: one-to-one (child)
    recipe = relationship("Recipe", back_populates="polish")
    # Brands to polishes: one-to-many (child)
    brand = relationship("Brand", back_populates="polish")
    # Polishes to swatch photos: one-to-many (parent)
    swatch_photo = relationship("SwatchPhoto", back_populates="polish")
    # Polishes to mani photos: many-to-many
    mani_photo = relationship(
        "ManiPhoto",
        secondary=polishes_mani_photos,
        back_populates="polish",
        lazy="dynamic",
    )
    # Polishes to order logs: many-to-many
    order_log = relationship(
        "OrderLog",
        secondary=polishes_order_logs,
        back_populates="polish",
        lazy="dynamic",
    )
    # Polishes to mani logs: many-to-many
    #mani_log = relationship(
    #    "ManiLog",
    #    secondary=polishes_mani_logs,
    #    back_populates="polish",
    #    lazy="dynamic",
    #)
    mani_associations = relationship(
        "PolishManiLog", back_populates="polish", cascade="all, delete-orphan"
    )
    mani_log = association_proxy("mani_associations", "mani_log")

    # Polishes to tags: many-to-many
    tag = relationship(
        "Tag",
        secondary=polishes_tags,
        back_populates="polish",
        lazy="dynamic"
    )

    # similarity self-referential relationship:
    similarity_links_1 = relationship(
        "SimilarTo",
        foreign_keys=[SimilarTo.polish_1_id],
        back_populates="polish_1",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )

    # links where I'm the larger id in the pair
    similarity_links_2 = relationship(
        "SimilarTo",
        foreign_keys=[SimilarTo.polish_2_id],
        back_populates="polish_2",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
    )

    @property
    def similarity_links(self):
        """All SimilarTo edges touching this polish."""
        return self.similarity_links_1 + self.similarity_links_2

    @property
    def similar_polishes(self):
        """All neighboring Polish objects (undirected), deduped."""
        neighbors = []
        for link in self.similarity_links_1:
            if link.polish_2 is not None:
                neighbors.append(link.polish_2)
        for link in self.similarity_links_2:
            if link.polish_1 is not None:
                neighbors.append(link.polish_1)
        return list({p.polish_id: p for p in neighbors}.values())

    def set_similarity(self, other):
        if self.id is None or other.id is None:
            raise ValueError("Both polishes must be committed before linking.")
        if self.id == other.id:
            raise ValueError("Cannot link a polish to itself.")

        a, b = sorted((self.id, other.id))

        # link.rank = rank # to add later

        link = db.session.get(SimilarTo, (a, b))
        if link is None:
            link = SimilarTo(polish_1_id=a, polish_2_id=b)
            db.session.add(link)
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                link = db.session.get(SimilarTo, (a, b))

        return link

    def remove_similarity(self, other):
        if self.id is None or other.id is None:
            return False
        if self.id == other.id:
            return False

        a, b = sorted((self.id, other.id))
        link = db.session.get(SimilarTo, (a, b))
        if link is None:
            return False

        db.session.delete(link)
        return True
    
# class: SwatchPhoto
# creates `swatch_photos` table
class SwatchPhoto(db.Model):
    __tablename__ = "swatch_photos"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    path = db.Column(db.String(255), nullable=False)

    # Foreign keys
    polish_id = db.Column(db.Integer, db.ForeignKey("polishes.id"), nullable=False)

    # Relationships
    # polishes to swatch_photos: one-to-many (child)
    polish = relationship("Polish", back_populates="swatch_photo")


# class: ManiPhoto
# creates `mani_photos` table
class ManiPhoto(db.Model):
    __tablename__ = "mani_photos"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    path = db.Column(db.String(255), nullable=False)

    # Foreign keys
    mani_log_id = db.Column(db.Integer, db.ForeignKey("mani_logs.id"), nullable=False)

    # Relationships
    # mani_logs to mani_photos: one-to-many (child)
    mani_log = relationship("ManiLog", back_populates="mani_photo")
    # mani_photos to polishes: many-to-many
    polish = relationship(
        "Polish",
        secondary=polishes_mani_photos,
        back_populates="mani_photo",
        lazy="dynamic",
    )


# class: OrderLog
# creates `order_logs` table
class OrderLog(db.Model):
    __tablename__ = "order_logs"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    order_date = db.Column(db.Date)
    vendor = db.Column(db.String(100))
    order_total = db.Column(db.Float)
    subtotal_polish = db.Column(db.Float)
    subtotal_ingredient = db.Column(db.Float)
    subtotal_other = db.Column(db.Float)
    subtotal_ship_tax = db.Column(db.Float)
    subtotal_discount = db.Column(db.Float)

    # Relationships
    # polishes to order_logs: many-to-many
    polish = relationship(
        "Polish",
        secondary=polishes_order_logs,
        back_populates="order_log",
        lazy="dynamic",
    )
    # ingredients to order_logs: many-to-many
    ingredient = relationship(
        "Ingredient",
        secondary=ingredients_order_logs,
        back_populates="order_log",
        lazy="dynamic",
    )


# class: ManiLog
# creates `mani_logs` table
class ManiLog(db.Model):
    __tablename__ = "mani_logs"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    mani_date = db.Column(db.Date)

    # Relationships
    # mani_logs to mani_photos: one-to-many (parent)
    mani_photo = relationship("ManiPhoto", back_populates="mani_log")

    # mani_logs to polishes: many-to-many
    #polish = relationship(
    #    "Polish",
    #    secondary=polishes_mani_logs,
    #    back_populates="mani_log",
    #    lazy="dynamic",
    #)
	# Mani logs to polishes: many-to-many
    polish_associations = relationship(
		"PolishManiLog", back_populates="mani_log", cascade="all, delete-orphan"
	)
    polish = association_proxy("polish_associations", "polish")

    # mani_logs to tags: many-to-many
        # tags to mani_logs: many-to-many
    tag = db.relationship(
        "Tag",
        secondary=mani_logs_tags,
        back_populates="mani_log",
        lazy="dynamic"
    )


# class: Ingredient
# creates `ingredients` table
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    name = db.Column(db.String(150), nullable=False)
    vendor = db.Column(db.String(150), nullable=False)
    # eventually add:
    # tags
    # qty_vol
    # qty_weight
    # particle_size

    # Relationships
    # ingredients to order_logs: many-to-many
    order_log = relationship(
        "OrderLog",
        secondary=ingredients_order_logs,
        back_populates="ingredient",
        lazy="dynamic",
    )
    # ingredients to recipes: many-to-many
    recipe = relationship(
        "Recipe",
        secondary=ingredients_recipes,
        back_populates="ingredient",
        lazy="dynamic",
    )


# class: Tag
# creates `tags` table
class Tag(db.Model):
    __tablename__ = "tags"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Core field
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationships
    # tags to polishes: many-to-many
    polish = db.relationship(
        "Polish",
        secondary=polishes_tags,
        back_populates="tag",
        lazy="dynamic"
    )

    # tags to mani_logs: many-to-many
    mani_log = db.relationship(
        "ManiLog",
        secondary=mani_logs_tags,
        back_populates="tag",
        lazy="dynamic"
    )
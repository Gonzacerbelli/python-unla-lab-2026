from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("sqlite:///database.db")
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)

    cart_items = relationship("CartItems", back_populates="product")


class Carts(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    creation_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)

    items = relationship("CartItems", back_populates="cart", cascade="all, delete-orphan")
    sales = relationship("Sales", back_populates="cart")


class CartItems(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    cart = relationship("Carts", back_populates="items")
    product = relationship("Products", back_populates="cart_items")


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), unique=True, nullable=False)
    total_price = Column(Float, nullable=False)

    cart = relationship("Carts", back_populates="sales")


Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)
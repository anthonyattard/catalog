from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Category(name="soccer")
session.add(category1)
session.commit()

category2 = Category(name="basketball")
session.add(category2)
session.commit()

category3 = Category(name="baseball")
session.add(category3)
session.commit()

category4 = Category(name="snowboarding")
session.add(category4)
session.commit()

category5 = Category(name="football")
session.add(category5)
session.commit()

category6 = Category(name="foosball")
session.add(category6)
session.commit()

category7 = Category(name="skating")
session.add(category7)
session.commit()

category8 = Category(name="hockey")
session.add(category8)
session.commit()

category9 = Category(name="field-hockey")
session.add(category9)
session.commit()

item1 = Item(name="Soccer Ball", 
     description="For practice or the big game, you need to be quick on your feet. Lace up the Nike Men Vapor Varsity Low TD Football Cleats and step out on the gridiron youll be ready to charge down the field in comfort and style.",
     category=category1,
     user_id=1)

session.add(item1)
session.commit()

item2 = Item(name="Soccer Cleats", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category1,
     user_id=1)

session.add(item2)
session.commit()

item3 = Item(name="Bball Band", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category2,
     user_id=1)

session.add(item3)
session.commit()

item4 = Item(name="Baseball Glove", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category3,
     user_id=1)

session.add(item4)
session.commit()

item5 = Item(name="Baseball Bat", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category3,
     user_id=1)

session.add(item5)
session.commit()

item6 = Item(name="Frisbee", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category4,
     user_id=1)

session.add(item6)
session.commit()

item7 = Item(name="Snowboard", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category5,
     user_id=1)

session.add(item7)
session.commit()

item8 = Item(name="Rock Climbing Gloves", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category6,
     user_id=1)

session.add(item8)
session.commit()

item9 = Item(name="Foosball Ball", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category7,
     user_id=1)

session.add(item9)
session.commit()

item10 = Item(name="Ice Skates", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category8,
     user_id=1)

session.add(item10)
session.commit()

item11 = Item(name="Hockey Stick", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category8,
     user_id=1)

session.add(item11)
session.commit()

item12 = Item(name="Field Hockey Ball", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category9,
     user_id=1)

session.add(item12)
session.commit()

item13 = Item(name="Ice Skate Laces", 
     description="Donec sed augue at eros bibendum aliquet in sit amet nunc. Maecenas fringilla dolor at sem lobortis, non porttitor felis lobortis. Integer non dolor vel neque eleifend consequat sit amet sit amet ligula.",
     category=category7,
     user_id=2)

session.add(item13)
session.commit()




# item1 = Item(name="Soccer Cleats", 
#              description="For practice or the big game, you need to be quick on your feet. Lace up the Nike Men Vapor Varsity Low TD Football Cleats and step out on the gridiron youll be ready to charge down the field in comfort and style.",
#              category=category1)

# session.commit()

# menuItem2 = MenuItem(name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
#                      price="$7.50", course="Entree", restaurant=restaurant1)
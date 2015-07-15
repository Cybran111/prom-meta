# coding=utf8

# представьте, что следующий словарь - база данных
# в дальнейших комментах под базой будет подразумеваться этот список

db = [
    {'id': 1, 'name': 'Chuck Norris', 'rate': 2},
    {'id': 2, 'name': 'Bruce Lee', 'rate': 1},
    {'id': 3, 'name': 'Jackie Chan', 'rate': 3},
]


class BaseField(type):
    _use_type = None


class Field(metaclass=BaseField):
    _value = None
    _field_name = None
    _model = None

    def __init__(self, field_name):
        self._field_name = field_name

    def __eq__(self, other):
        return '"{}"."{}" = \'{}\''\
            .format(self._model.__tablename__, self._field_name, other)

    def __get__(self, instance, owner):
        if self._model is None:
            self._model = owner

        if instance is None:
            return self
        return instance._entry[self._field_name]

    def __set__(self, instance, value):
        self._value = self._use_type(value)
        instance._entry[self._field_name] = self._use_type(value)


class BaseModel(type):
    __tablename__ = None
    __id_field = None
    __fields = None

    @staticmethod
    def __serial():
        i = max(db, key=lambda item: item['id'])['id']
        while True:
            i += 1
            yield i

    def __new__(mcs, name, bases, attrs):
        if "id" in attrs:
            raise Exception("You cannot use this name for field")

        attrs['_id_serial'] = mcs.__serial()

        return super(BaseModel, mcs).__new__(mcs, name, bases, attrs)


class Entity(metaclass=BaseModel):
    _entry = None

    def __init__(self, entry=None, *args, **kwargs):
        if entry is None:
            self._entry = dict()
            self._entry['id'] = next(self._id_serial)

            for name, value in kwargs.items():
                setattr(self, name, value)

            db.append(self._entry)

        else:
            self._entry = entry

        super(Entity, self).__init__()

    @classmethod
    def get(cls, id_):
        entry = next(filter(lambda entry: entry["id"] == id_, db))
        return cls(entry=entry)

    def __getattr__(self, field_name):
        return self.__dict__[field_name]


class TextField(Field):
    _use_type = str


class IntegerField(Field):
    _use_type = int


# Делаем мини-модель ORM, нужно заставить работать следующий кусок кода.
# Для этого реализуйте объявленные выше классы, а также, если необходимо,
# базовые и метаклассы.

class User(Entity):
    __tablename__ = 'user'
    name = TextField("name")
    rate = IntegerField("rate")

user = User(name="baka", rate=5)

# если угодно, можно заменить TextField на Field(Text), Field.Text и т.п.

u = User.get(2)                   # u должен присвоиться объект типа User
#                                 # с аттрибутами id=2,
#                                 # name='Bruce Lee', rate=1

assert u.name == "Bruce Lee"    # вернет строку 'Bruce Lee'
#
u2 = User(name='Arni', rate=4)  # В "базу" должен записаться новый dict
#                                 # {'id': 4, 'name': 'Arni', 'rate': 4},
#                                 # переменной u2 должен присвоиться объект
#                                 # типа User c аттрибутами
#                                 # name='Arni', rate=4
#
#
# u2.rate                         # Должно вернуть 4 (int(4))
assert u2.rate == 4
#
# User.name == 'Duncan MacLeod'   # Выражение должно вернуть SQL statement
#                                 # (просто строку):
#                                 # "user"."name" = 'Duncan MacLeod'
#
assert (User.name == 'Duncan MacLeod') == "\"user\".\"name\"" \
                                          " = 'Duncan MacLeod'"

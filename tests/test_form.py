import datetime

import formidable as f


def test_text_field():
    class TestForm(f.Form):
        fullname = f.TextField()
        lorem = f.TextField(default="ipsum")

    form = TestForm({"fullname": ["John Doe"]})

    assert form.fullname.name == "fullname"
    assert form.fullname.value == "John Doe"
    assert form.lorem.value == "ipsum"

    data = form.save()
    print(data)
    assert data == {
        "fullname": "John Doe",
        "lorem": "ipsum",
    }


def test_integer_field():
    class TestForm(f.Form):
        age = f.IntegerField()
        min_age = f.IntegerField(default=18)

    form = TestForm({"age": ["20"]})

    assert form.age.name == "age"
    assert form.age.value == 20
    assert form.min_age.value == 18

    data = form.save()
    print(data)
    assert data == {
        "age": 20,
        "min_age": 18,
    }


def test_float_field():
    class TestForm(f.Form):
        x = f.FloatField()
        y = f.FloatField()
        z = f.FloatField(default=0)

    form = TestForm(
        {
            "x": ["20"],
            "y": ["15.5"],
        }
    )

    assert form.x.name == "x"
    assert form.x.value == 20.0
    assert form.y.value == 15.5
    assert form.z.value == 0.0

    data = form.save()
    print(data)
    assert data == {
        "x": 20.0,
        "y": 15.5,
        "z": 0.0,
    }


def test_boolean_field():
    class TestForm(f.Form):
        alive = f.BooleanField(default=True)
        owner = f.BooleanField(default=False)
        admin = f.BooleanField()
        alien = f.BooleanField()

    form = TestForm(
        {
            "admin": ["1"],
            "alien": [""],
        }
    )

    assert form.alive.name == "alive"
    assert form.alive.value is True
    assert form.owner.value is False
    assert form.admin.value is True
    assert form.alien.value is False

    data = form.save()
    print(data)
    assert data == {
        "alive": True,
        "owner": False,
        "admin": True,
        "alien": False,
    }


def test_list_field():
    class TestForm(f.Form):
        tags = f.ListField()
        friends = f.ListField(type=int)
        wat = f.ListField()

    form = TestForm(
        {
            "tags[]": ["python", "formidable", "testing"],
            "friends[]": ["1", "2", "3"],
        }
    )

    assert form.tags.name == "tags[]"
    assert form.tags.value == ["python", "formidable", "testing"]

    assert form.friends.name == "friends[]"
    assert form.friends.value == [1, 2, 3]

    assert form.wat.name == "wat[]"
    assert form.wat.value == []

    data = form.save()
    print(data)
    assert data == {
        "tags": ["python", "formidable", "testing"],
        "friends": [1, 2, 3],
        "wat": [],
    }


def test_date_field():
    class TestForm(f.Form):
        birthday = f.DateField()
        anniversary = f.DateField(default="2020-01-01")

    form = TestForm({"birthday": ["1990-05-15"]})

    assert form.birthday.name == "birthday"
    assert form.birthday.value == datetime.date(1990, 5, 15)
    assert form.anniversary.value == datetime.date(2020, 1, 1)

    data = form.save()
    print(data)
    assert data == {
        "birthday": datetime.date(1990, 5, 15),
        "anniversary": datetime.date(2020, 1, 1),
    }


def test_datetime_field():
    class TestForm(f.Form):
        created = f.DateTimeField()
        updated = f.DateTimeField(default="2024-06-05T12:34:56")

    form = TestForm({"created": ["2025-06-05T08:30:00"]})

    assert form.created.name == "created"
    assert form.created.value == datetime.datetime(2025, 6, 5, 8, 30)
    assert form.updated.value == datetime.datetime(2024, 6, 5, 12, 34, 56)

    data = form.save()
    print(data)
    assert data == {
        "created": datetime.datetime(2025, 6, 5, 8, 30),
        "updated": datetime.datetime(2024, 6, 5, 12, 34, 56),
    }


def test_time_field():
    class TestForm(f.Form):
        start = f.TimeField()
        end = f.TimeField(default="17:00:00")

    form = TestForm({"start": ["09:15:00"]})

    assert form.start.name == "start"
    assert form.start.value == datetime.time(9, 15, 0)
    assert form.end.value == datetime.time(17, 0, 0)

    data = form.save()
    print(data)
    assert data == {
        "start": datetime.time(9, 15, 0),
        "end": datetime.time(17, 0, 0),
    }


def test_form_field():
    class AddressForm(f.Form):
        street = f.TextField()
        city = f.TextField()

    class TestForm(f.Form):
        address = f.FormField(AddressForm)

    form = TestForm(
        {
            "address[street]": ["123 Main St"],
            "address[city]": ["Springfield"],
        }
    )

    assert form.address.form.street.name == "address[street]"
    assert form.address.form.street.value == "123 Main St"

    assert form.address.form.city.name == "address[city]"
    assert form.address.form.city.value == "Springfield"

    data = form.save()
    print(data)
    assert data == {
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
        }
    }


def test_formset_field():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.FormSet(SkillForm)

    form = TestForm(
        {
            "skills[0][name]": ["Python"],
            "skills[0][level]": ["5"],
            "skills[1][name]": ["JavaScript"],
            "skills[1][level]": ["3"],
        }
    )

    assert form.skills.form.name.name == "skills[NEW_INDEX][name]"
    assert form.skills.form.level.name == "skills[NEW_INDEX][level]"

    # assert form.skills.forms[0].name.name == "skills[0][name]"
    # assert form.skills.forms[0].name.value == "Python"

    # assert form.skills.forms[0].level.name == "skills[0][level]"
    # assert form.skills.forms[0].level.value == 5

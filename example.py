import formidable as f


class SkillForm(f.Form):
    name = f.TextField()
    level = f.IntegerField(default=1)


class AddressForm(f.Form):
    street = f.TextField()
    city = f.TextField()


class UserForm(f.Form):
    name =  f.TextField()
    friends = f.ListField(type=int)
    active = f.BooleanField(default=False)
    skills = f.FormSet(SkillForm)
    address = f.FormField(AddressForm)


# You would use the request POST data of your web framework instead,
# for example `request_data = request.form` in Flask
request_data = {
    "name": ["John Doe"],
    "friends[]": ["2", "3"],
    "address[street]": ["123 Main St"],
    "address[city]": ["Anytown"],
}

# The magic
form = UserForm(request_data, object=None)

print(form)
# UserForm(name='John Doe', friends=[2, 3], active=False)

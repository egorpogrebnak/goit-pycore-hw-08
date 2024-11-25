from functools import wraps
from collections import UserDict
from datetime import datetime, timedelta
import pickle


def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт не знайдено"
        except ValueError:
            return "Хибний формат, перевірте кількість аргументів"
        except IndexError:
            return "Хибний формат, перевірте кількість аргументів"
    return wrapper


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must have exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError(f"Phone number {phone} not found.")

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                self.phones.remove(p)
                self.phones.append(Phone(new_phone))
                return
        raise ValueError(f"Phone number {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ', '.join([phone.value for phone in self.phones])
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Not set"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record with name {name} not found.")

    def get_upcoming_birthdays(self, days=7):
        date_today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_day = record.birthday.value
                upcoming_birth = datetime(date_today.year, birthday_day.month, birthday_day.day).date()

                if upcoming_birth < date_today:
                    upcoming_birth = datetime(date_today.year + 1, birthday_day.month, birthday_day.day).date()

                days_left = (upcoming_birth - date_today).days

                if 0 <= days_left <= days:
                    if upcoming_birth.weekday() > 4: 
                        congratulation_date = upcoming_birth + timedelta(days=(7 - upcoming_birth.weekday()))
                    else:
                        congratulation_date = upcoming_birth

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays

@input_error
def add_contact(args, address_book):
    name, phone, *_ = args
    birthday = args[2] if len(args) > 2 else None
    record = address_book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        address_book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    if birthday:
            record.add_birthday(birthday)
    return message

@input_error
def change_contact(args, address_book):
    name, old_phone, new_phone = args
    record = address_book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Contact {name} updated phone {old_phone} to {new_phone}."
    else:
        return "Contact not found."

@input_error
def show_phone(args, address_book):
    name = args[0]
    record = address_book.find(name)
    if record:
        return str(record)
    else:
        return "Contact not found."

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday {birthday} added for contact {name}."
    else:
        return "Contact not found."
    
@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    elif record:
        return f"No birthday set for {name}."
    else:
        return "Contact not found."

@input_error
def birthdays(address_book, days=7):

    upcoming = address_book.get_upcoming_birthdays(days)
    if upcoming:
        result = "\n".join([
            f"{record['name']} - Congratulations on {record['congratulation_date']}"
            for record in upcoming
        ])
        return result
    return f"No birthdays in the next {days} days."

def show_all(address_book):
    if address_book.data:
        return "\n".join([str(record) for record in address_book.data.values()])
    else:
        return "No contacts available."



def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()



def main():
    address_book = load_data()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        cmd, *args = user_input.strip().split()

        if cmd in ["close", "exit"]:
            print("Good bye!")
            save_data(address_book)
            break
        elif cmd == "hello":
            print("How can I help you?")
        elif cmd == "add":
            print(add_contact(args, address_book))
        elif cmd == "change":
            print(change_contact(args, address_book))
        elif cmd == "phone":
            print(show_phone(args, address_book))
        elif cmd == "all":
            print(show_all(address_book))
        elif cmd == "add-birthday":
            print(add_birthday(args, address_book))
        elif cmd == "show-birthday":
            print(show_birthday(args, address_book))
        elif cmd == "birthdays":
            print(birthdays(address_book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

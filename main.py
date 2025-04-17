import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # or 'sdl2' or 'gl'

import firebase_admin
from firebase_admin import credentials, db

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# ----------------- Firebase Setup -------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/AKASH/Desktop/practice/booklistapp-ff17b-firebase-adminsdk-fbsvc-5110401e0e.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://booklistapp-ff17b-default-rtdb.firebaseio.com'
    })

# ----------------- Screens -------------------
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="Welcome to Akash vishwakarma's \n Book List App!", font_size=24))

        signup_btn = Button(text='Sign Up',height=50)
        signup_btn.bind(on_press=self.switch_to_signup)
        layout.add_widget(signup_btn)

        login_btn = Button(text='Login',height=50)
        login_btn.bind(on_press=self.switch_to_login)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def switch_to_signup(self, instance):
        self.manager.current = 'signup'

    def switch_to_login(self, instance):
        self.manager.current = 'login'


class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.username = TextInput(hint_text='Username')
        self.password = TextInput(hint_text='Password', password=True)
        self.message = Label(text='')

        signup_btn = Button(text='Create Account',height=50)
        signup_btn.bind(on_press=self.create_account)

        self.layout.add_widget(self.username)
        self.layout.add_widget(self.password)
        self.layout.add_widget(signup_btn)
        self.layout.add_widget(self.message)

        back_btn = Button(text='Back',height=50)
        back_btn.bind(on_press=self.switch_to_welcome)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def create_account(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        if user and pwd:
            ref = db.reference('users')
            ref.child(user).set({
                'username': user,
                'password': pwd
            })
            self.message.text = 'Account created!'
        else:
            self.message.text = 'Please enter valid details.'

    def switch_to_welcome(self, instance):
        self.manager.current = 'welcome'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.username = TextInput(hint_text='Username')
        self.password = TextInput(hint_text='Password', password=True)
        self.message = Label(text='')

        login_btn = Button(text='Login',height=50)
        login_btn.bind(on_press=self.check_login)

        self.layout.add_widget(self.username)
        self.layout.add_widget(self.password)
        self.layout.add_widget(login_btn)
        self.layout.add_widget(self.message)

        back_btn = Button(text='Back',height=50)
        back_btn.bind(on_press=self.switch_to_welcome)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def check_login(self, instance):
        user = self.username.text.strip()
        pwd = self.password.text.strip()

        ref = db.reference('users')
        user_data = ref.child(user).get()

        if user_data and user_data['password'] == pwd:
            self.manager.current = 'booklist'
        else:
            self.message.text = 'Invalid credentials.'

    def switch_to_welcome(self, instance):
        self.manager.current = 'welcome'


class AddBookScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.book_title = TextInput(hint_text='Book Title')
        self.book_details = TextInput(hint_text='Book Details')
        self.message = Label(text='')

        add_btn = Button(text='Add Book')
        add_btn.bind(on_press=self.add_book)

        self.layout.add_widget(self.book_title)
        self.layout.add_widget(self.book_details)
        self.layout.add_widget(add_btn)
        self.layout.add_widget(self.message)

        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.switch_to_booklist)  # Ensure this switches back to the book list screen
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def add_book(self, instance):
        title = self.book_title.text.strip()
        details = self.book_details.text.strip()

        if title and details:
            # Reference to 'books' in Firebase
            ref = db.reference('books')

            # Check if the book already exists by title
            existing_book = ref.order_by_child('name').equal_to(title).get()

            if existing_book:
                # If the book already exists, show a message
                self.message.text = 'This book already exists in the list.'
            else:
                # If the book doesn't exist, add it to Firebase
                ref.push().set({
                    'name': title,
                    'details': details,
                    'uploader': uploader_uid
                })
                self.message.text = 'Book added successfully!'
                self.manager.get_screen('booklist').load_books()  # Refresh book list after adding
                self.switch_to_booklist(instance)  # Optionally, you can switch to book list screen after adding
        else:
            self.message.text = 'Please enter valid details.'

    def switch_to_booklist(self, instance):
        # Switch to the book list screen after adding a book or pressing back
        self.manager.current = 'booklist'



class BookListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.layout.add_widget(Label(text='Online Book List', font_size=20))

        # Scrollview to hold books
        self.scroll = ScrollView()
        self.book_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.book_layout.bind(minimum_height=self.book_layout.setter('height'))

        self.scroll.add_widget(self.book_layout)
        self.layout.add_widget(self.scroll)

        # Button layout for Add New Book and Browse buttons
        button_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)

        # Add New Book Button
        add_book_btn = Button(text='Add New Book', size_hint_x=0.5, width=150, height=50)
        add_book_btn.bind(on_press=self.switch_to_addbook)  # You can bind this to switch to the Add Book screen
        button_layout.add_widget(add_book_btn)

        # Browse Button
        browse_button = Button(text='Browse')
        browse_button.bind(on_press=self.show_browse_popup)
 # Implement this method later for browsing functionality
        button_layout.add_widget(browse_button)

        # Add the button layout with Add and Browse buttons
        self.layout.add_widget(button_layout)

        # Logout Button
        logout_btn = Button(text='Logout', size_hint_y=None, height=40)
        logout_btn.bind(on_press=self.switch_to_welcome)  # Switch back to the Welcome screen
        self.layout.add_widget(logout_btn)

        # Add the complete layout to the screen
        self.add_widget(self.layout)

        # Load books when this screen is displayed
        self.load_books()

    def load_books(self):
        # Here you can add logic to fetch and display books from Firebase
        pass

    def switch_to_welcome(self, instance):
        # Switch back to the Welcome screen
        self.manager.current = 'welcome'

    def load_books(self):
        # Clear current books before loading new ones
        self.book_layout.clear_widgets()

        demo_books = db.reference('books').get()

        if demo_books:
            for book_id, book in demo_books.items():
                book_label = Button(text=book['name'], size_hint_y=None, height=40)
                book_label.bind(on_press=lambda x, book_id=book_id: self.view_book(book_id))
                self.book_layout.add_widget(book_label)
        else:
            self.book_layout.add_widget(Label(text="No books found!", size_hint_y=None, height=40))

    def view_book(self, book_id):
        self.manager.current = 'bookdetail'
        self.manager.get_screen('bookdetail').load_book_details(book_id)

    def switch_to_addbook(self, instance):
        self.manager.current = 'addbook'

    def switch_to_welcome(self, instance):
        self.manager.current = 'welcome'

    def show_browse_popup(self,instance):
        self.manager.current = 'browsepage'

class BookDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.title_label = Label(text='Book Title', font_size=24)
        self.details_label = Label(text='Book Details')

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.details_label)

        back_btn = Button(text='Back',height=50)
        back_btn.bind(on_press=self.switch_to_booklist)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def load_book_details(self, book_id):
        ref = db.reference(f'books/{book_id}')
        book = ref.get()

        if book:
            self.title_label.text = f"Title: {book['name']}"
            self.details_label.text = f"Details: {book['details']}"
        else:
            self.title_label.text = 'Book not found!'
            self.details_label.text = ''

    def switch_to_booklist(self, instance):
        self.manager.current = 'booklist'

    def Browse_page(self, instance):
        self.manager.current='browse'
        
def show_browse_popup(self, instance):
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label

    layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
    scroll = ScrollView()

    list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
    list_layout.bind(minimum_height=list_layout.setter('height'))

    # Fetch data from Firebase
    books_data = db.child("books").get().val()
    if books_data:
        for key, book in books_data.items():
            title = book.get('title', 'Untitled')
            description = book.get('description', 'No description')
            book_label = Label(text=f"[b]{title}[/b]\n{description}", markup=True, size_hint_y=None, height=80)
            list_layout.add_widget(book_label)
    else:
        list_layout.add_widget(Label(text="No books available."))

    scroll.add_widget(list_layout)
    layout.add_widget(scroll)

    close_btn = Button(text="Close", size_hint_y=None, height=40)
    close_btn.bind(on_press=lambda x: popup.dismiss())
    layout.add_widget(close_btn)

    popup = Popup(title="Browse Books", content=layout, size_hint=(0.9, 0.9))
    popup.open()

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from firebase_admin import db

class BrowseScreen(Screen):
    def __init__(self, current_user_email, **kwargs):
        super().__init__(**kwargs)
        self.current_user_email = current_user_email  # Store the current user's email

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Add Search Bar
        self.search_input = TextInput(
            hint_text='Search books by title...',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.search_input.bind(text=self.on_search)
        layout.add_widget(self.search_input)

        # Scrollable area
        self.scroll = ScrollView()
        self.book_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.book_list_layout.bind(minimum_height=self.book_list_layout.setter('height'))
        self.scroll.add_widget(self.book_list_layout)
        layout.add_widget(self.scroll)

        # Back Button
        back_btn = Button(text='Back', size_hint_y=None, height=50)
        back_btn.bind(on_press=self.switch_to_booklist)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.load_books()

    def load_books(self, search_term=""):
        self.book_list_layout.clear_widgets()

        def fetch_books(*args):
            books_data = db.reference('books').get()

            found = False
            if books_data:
                for key, book in books_data.items():
                    title = book.get('name', 'Untitled')
                    description = book.get('details', 'No description')

                    if search_term.lower() in title.lower():
                        found = True
                        book_button = Button(
                            text=f"[b]{title}[/b]",
                            markup=True,
                            size_hint_y=None,
                            height=80
                        )
                        book_button.bind(on_press=lambda instance, book_id=key: self.view_book_details(book_id))
                        self.book_list_layout.add_widget(book_button)

                        chat_button = Button(
                            text="Chat with uploader",
                            size_hint_y=None,
                            height=40
                        )
                        chat_button.bind(on_press=lambda instance, book_id=key: self.open_chat_screen(book_id))
                        self.book_list_layout.add_widget(chat_button)

            if not found:
                self.book_list_layout.add_widget(Label(text="No books found!", size_hint_y=None, height=40))

        Clock.schedule_once(fetch_books, 0)

    def on_search(self, instance, value):
        self.load_books(search_term=value)

    def view_book_details(self, book_id):
        self.manager.current = 'bookdetail'
        self.manager.get_screen('bookdetail').load_book_details(book_id)

    def open_chat_screen(self, book_id):
        # Pass the current user's email when opening the chat screen
        self.manager.get_screen('chatscreen').open_chat_screen(book_id, self.current_user_email)

    def switch_to_booklist(self, instance):
        self.manager.current = 'booklist'



class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.chat_box = BoxLayout(orientation='vertical', size_hint_y=0.9)
        self.input = TextInput(size_hint_y=0.1, multiline=False)
        self.send_btn = Button(text='Send', size_hint_y=0.1)
        self.send_btn.bind(on_press=self.send_message)

        self.back_btn=Button(text='Back',size_hint_y=0.1)
        self.back_btn.bind(on_press=self.back_from_message)

        self.layout.add_widget(self.back_btn)

        self.layout.add_widget(self.chat_box)
        self.layout.add_widget(self.input)
        self.layout.add_widget(self.send_btn)
        self.add_widget(self.layout)

        self.current_user_email = ""  # <--- Add this

    def load_chat(self, book_id, user_email):
        self.book_id = book_id
        self.current_user_email = user_email  # Store the email here

    def send_message(self, instance):
        text = self.input.text.strip()
        if text:
            ref = db.reference(f'chats/{self.book_id}')
            ref.push().set({
                'user': self.current_user_email,  # Use the stored email here
                'text': text
            })
            self.load_chat(self.book_id, self.current_user_email)  # Reload the chat after sending
            self.input.text = ""  # Clear the input box

    def open_chat_screen(self, book_id, user_email):
        self.manager.get_screen('chatscreen').load_chat(book_id, user_email)
        self.manager.current = 'chatscreen'

    def back_from_message(self,instance):
        self.manager.current='booklist'


# ---------------- App -------------------
class BookApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Example: Assume we get the current_user_email after login or signup
        current_user_email = "user@example.com"  # Replace with the actual user's email

        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(BookListScreen(name='booklist'))
        sm.add_widget(AddBookScreen(name='addbook'))
        sm.add_widget(BookDetailScreen(name='bookdetail'))
        sm.add_widget(BrowseScreen(name='browsepage', current_user_email=current_user_email))  # Pass email here
        sm.add_widget(ChatScreen(name='chatscreen'))

        return sm

BookApp().run()

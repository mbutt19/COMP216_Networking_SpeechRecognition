import speech_recognition
import pyttsx3
from selenium import webdriver
from bs4 import BeautifulSoup
import pycountry
import requests
import random
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
import os

path = os.path.join(os.path.dirname(__file__))

MainWindowUI, MainWindowBase = uic.loadUiType(
    os.path.join(path, 'form.ui'))


class SpeechWebScraper(MainWindowBase, MainWindowUI):

    def __init__(self, parent=None):
        MainWindowBase.__init__(self, parent)

        self.setupUi(self)
        # Create a variable that will represent as robot app to communicate with the user, just like Siri
        self.robot = speech_recognition.Recognizer()
        # Create a variable for speaking using pyttsx module
        self.audio = pyttsx3.init()
        # Create a self.robot voice to communicate with the user
        self.voices = self.audio.getProperty('voices')
        self.audio.setProperty('voices', self.voices[0].id)
        self.pushButton_start.clicked.connect(self.menu_selection)
        self.pushButton_stop.clicked.connect(self.stop_event)
        self.textBrowser_conversation.append("""
                ┼┼┼┼┼┼┼┼┼┼┼┼▄▀▀▀▄▄▄▄▄▄▄▀▀▀▄┼┼┼┼┼┼┼┼┼┼┼
                ┼┼┼┼┼┼┼┼┼┼┼┼█▒▒░░░░░░░░░▒▒█┼┼┼┼┼┼┼┼┼┼┼
                ┼┼┼┼┼┼┼┼┼┼┼┼┼█░░█░░░░░█░░█┼┼┼┼┼┼┼┼┼┼┼┼
                ┼┼┼┼┼┼┼┼┼─▄▄──█░░░▀█▀░░░█──▄▄─┼┼┼┼┼┼┼┼
                ┼┼┼┼┼┼┼┼┼█░░█─▀▄░░░░░░░▄▀─█░░█┼┼┼┼┼┼┼┼
                ┼┼┼┼┼┼██░██░████░██░░░██░░░█████┼┼┼┼┼┼
                ┼┼┼┼┼┼██▄██░██▄▄░██░░░██░░░██░██┼┼┼┼┼┼
                ┼┼┼┼┼┼██▀██░██▀▀░██░░░██░░░██░██┼┼┼┼┼┼
                ┼┼┼┼┼┼██░██░████░████░████░█████┼┼┼┼┼┼
        """)
        self.continueLoop = True

    # Create a function to read the words and say it out loud
    def ROBOT_VOICE(self, words):
        self.audio.say(words)
        self.audio.runAndWait()

    # Create function to scrape weather data from the web, takes country & city parameters, & returns forecast as string
    def weather_scraper(self, country: str, city: str):
        # Variable holds path to webdriver for selenium use
        PATH = "./chromedriver.exe"
        # Create variable to store url with country and city appended which will be opened
        URL = 'https://www.timeanddate.com/weather/' + country + '/' + city
        # Option variable to pass driver object to suppress the opening of the browser
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        # Variable represents Chrome browser
        driver = webdriver.Chrome(PATH, options=option)
        # Webdriver opens url
        driver.get(URL)
        # Page loads generates full code, source code is then stored as a variable
        soup_source = driver.page_source
        # Variable creates a soup object based on source code in analyzable format
        soup = BeautifulSoup(soup_source, features="lxml")
        # Webdriver closed as beautifulsoup will process remaining code
        driver.quit()
        # Web page's title was a good format so I grabbed it as is
        title = soup.title.text.strip()
        # Element id of HTML code block needed to analyze
        focus = soup.find(id='qlook')
        # Variables to store extracted weather details
        temp = focus.find('div', class_='h2').text.strip()
        rest_info = focus.find_all('p')
        condition = rest_info[0].text.strip()
        description = rest_info[1].text.strip().split('F')
        # Create a formatted string variable to return forecast in speakable form
        feels = 'F' + description[1]
        return_string = f'{title}\n {temp}\nCondition is {condition}\n {feels}'
        return return_string

        # Method to statically web scrape time from user input of country & city
    def time_scraper(self, country: str, city: str):
        # Create variable to store url with country and city appended which will be opened
        URL = 'https://www.timeanddate.com/worldclock/' + country + '/' + city
        # Request gets page's full code
        page = requests.get(URL)
        # Variable creates a soup object based on source code in analyzable format
        soup = BeautifulSoup(page.content, features="lxml")
        # Web page's title was a good format so I grabbed it as is
        title = soup.title.text.strip()
        # Variables to store extracted weather details
        time = soup.find(id='ct').text.strip()
        time_zone = soup.find(id='cta').find('a')['title']
        return f'{title}\n is {time}\nTime Zone is {time_zone}'

    def time_module(self):
        # Try condition wraps entire module to cover microphone connectivity issues & unspecified errors
        try:
            # Create a string word for entry of the app and introduction for the user to know that the app is running
            self.general_display('Hey this is a Time app by Group 1! I can tell time anywhere.')
            with speech_recognition.Microphone() as source:
                while True:
                    try:
                        # Get country and city from the user with method, and assign to variables
                        country, city = self.location_getter(source)
                        self.general_display("let me get the time there")
                        if self.time_scraper(country, city):
                            scraped = self.time_scraper(country, city)
                            self.general_display(scraped)
                        else:
                            raise LookupError
                    except LookupError or AttributeError:
                        # Raised if city or country is not recognized in the url
                        self.general_display("Invalid city")
                    except speech_recognition.UnknownValueError:
                        # Raised if speech not recognized
                        self.general_display("Please Say a City")
                    except:
                        # Raised if other error
                        self.general_display("Something went wrong. Please try again")

                    # Ask the user to continue checking other locations for time
                    self.general_display("Would you like the time of another place? Yes or No? I'm listening...")
                    try:
                        listen = self.robot.listen(source)
                        command = self.robot.recognize_google(listen)
                        if "no" in command or "exit" in command or "stop" in command or 'nop' in command or 'cancel' in command or 'end' in command:
                            self.textBrowser_conversation.append(f"\nUser> {command}\n")
                            break
                        else:
                            self.general_display('I see!')
                    except speech_recognition.UnknownValueError:
                        self.general_display("Let's Continue")
        except speech_recognition.UnknownValueError:
            # Generic exception block without error type catches all unspecified errors & mic speech_recognition errors
            self.err_msg()

    # Speech-recognition and weather scraper functionality combined in weather_module
    def weather_module(self):
        # Try condition wraps entire module to cover microphone connectivity issues & unspecified errors
        try:
            # Create a string word for entry of the app and introduction for the user to know that the app is running
            self.general_display('Hey this is a Weather app by Group 1! I am here for your weather update.')
            with speech_recognition.Microphone() as source:
                while True:
                    try:
                        # Get country and city from the user with method, and assign to variables
                        country, city = self.location_getter(source)
                        self.general_display("let me get the weather there")
                        if self.weather_scraper(country, city):
                            scraped = self.weather_scraper(country, city)
                            self.general_display(scraped)
                        else:
                            raise LookupError
                    except LookupError or AttributeError:
                        # Raised if city or country is not recognized in the url
                        self.general_display("Invalid city")
                    except speech_recognition.UnknownValueError:
                        # Raised if speech not recognized
                        self.general_display("Please Say a City")
                    except:
                        # Raised if other error
                        self.general_display("Something went wrong. Please try again")
                    # Ask the user to continue checking other locations for weather updates
                    self.general_display("Would you like to check weather somewhere else? Yes or No? I'm listening...")
                    try:
                        listen = self.robot.listen(source)
                        command = self.robot.recognize_google(listen)
                        if "no" in command or "exit" in command or "stop" in command or 'nop' in command or 'cancel' \
                                in command or 'end' in command:
                            self.textBrowser_conversation.append(f"\nUser> {command}\n")
                            break
                        else:
                            self.general_display('I see!')
                    except speech_recognition.UnknownValueError:
                        self.general_display("Let's Continue")
        except:
            # Generic exception block w/o error type catches all unspecified errors and mic speech_recognition errors
            self.err_msg()

    def joke_module(self, source):
        self.continueJoke = True
        while self.continueJoke:
            response = requests.get("https://official-joke-api.appspot.com/random_joke").json()
            self.general_display(f"\nHere is your joke for today.\n")
            joke = f"{response['setup']} \n\n{response['punchline']}"
            self.general_display(joke)
            self.general_display("Would you like to hear another joke?")
            listen = self.robot.listen(source)
            command = self.robot.recognize_google(listen)
            if "no" in command or "exit" in command or "stop" in command or 'nope' in command or '5' in command \
                    or 'five' in command or 'nop' in command or 'cancel' in command or 'end' in command:
                self.continueJoke = False
                self.textBrowser_conversation.append(f"\nUser> {command}")

    def game_module(self, source):
        while True:
            num_guess = 0
            number = random.randint(1, 20)  # returns random integer within range
            # print the number so you can see it
            print(number)
            self.general_display('I am thinking of a number between 1 and 20.')
            self.general_display("How many attempts would you like to guess the number? I'm listening ...")
            listen = self.robot.listen(source)
            attempts = self.robot.recognize_google(listen)
            attempts = int(attempts)
            self.textBrowser_conversation.append(f'\nUser> {attempts}')
            guess = 0
            while num_guess < attempts:
                try:
                    self.general_display("Guess a number. I'm listening ")
                    listen = self.robot.listen(source)
                    guess = self.robot.recognize_google(listen)
                    guess = int(guess)
                    self.textBrowser_conversation.append(f'\nUser> {guess}')
                    num_guess += 1
                    if guess < number:
                        self.general_display('Your guess is too low.')
                    if guess > number:
                        self.general_display('Your guess is too high.')
                    if guess == number:
                        self.win_msg(num_guess)
                        break
                except:
                    # Generic exception block w/o error type catch all errors & mic speech_recognition errors
                    self.general_display("Something went Wrong. Please try again!")
            if guess != number:
                number = str(number)
                self.lose_msg(number)
            # Ask the user to continue checking other locations for weather updates
            self.general_display("Would you like to play another round? Yes or No? I'm listening...")
            try:
                listen = self.robot.listen(source)
                command = self.robot.recognize_google(listen)
                if "no" in command or "exit" in command or "stop" in command or 'nop' in command or 'cancel' in command or 'end' in command:
                    self.textBrowser_conversation.append(f"\nUser> {command}\n")
                    break
                else:
                    self.general_display('I see!')
            except speech_recognition.UnknownValueError:
                self.general_display("Let's Continue")

    def stop_event2(self):
        # self.stop_event2()
        self.general_display("Would you like to continue? Yes or No? I'm listening...")
        try:
            with speech_recognition.Microphone() as source:
                listen = self.robot.listen(source)
                command = self.robot.recognize_google(listen)
                if "no" in command or "exit" in command or "stop" in command or 'nop' in command or 'cancel' in command or 'end' in command:
                    self.continueLoop = False
                    self.textBrowser_conversation.append(f"\nUser> {command}")
                    # Closing message
                    self.exit_msg()
                else:
                    self.continueLoop = True
                    self.general_display("Let's continue! You can select from options on the left, I'm listening")
        except:
            # Generic exception block w/o error type catches all unspecified errors and mic speech_recognition errors
            self.err_msg()

    def stop_event(self):
        if self.continueLoop:
            self.continueLoop = False

    def menu_selection(self):
        self.general_display("What would you like to do today? You can select from options on the left, I'm listening")
        try:
            with speech_recognition.Microphone() as source:
                while self.continueLoop:
                    listen = self.robot.listen(source)
                    command = self.robot.recognize_google(listen)
                    if "no" in command or "exit" in command or "stop" in command or 'nope' in command or '5' in command \
                            or 'five' in command or 'nop' in command or 'cancel' in command or 'end' in command:
                        self.continueLoop = False
                        self.textBrowser_conversation.append(f"\nUser> {command}")
                        self.exit_msg()
                    elif "weather" in command or "get the weather" in command or "1" in command or "one" in command:
                        self.continueLoop = True
                        self.general_display("You selected to get the weather...")
                        self.weather_module()
                    elif "time" in command or "get the time" in command or "3" in command or "three" in command:
                        self.continueLoop = True
                        self.general_display("You selected to get the time...")
                        self.time_module()
                    elif "game" in command or "play a game" in command or "play" in command or "2" in command or "two" in command:
                        self.continueLoop = True
                        self.general_display("You selected to play a game...")
                        self.game_module(source)
                    elif "joke" in command or "tell me a joke" in command or "please tell me a joke" in command or "4" in command or "four" in command:
                        self.joke_module(source)
                    else:
                        self.continueLoop = True
                        self.general_display('I did not understand so I will tell you a joke!')
                        self.joke_module()

                    self.stop_event2()
        except:
            # Generic exception block without error type catches all unspecified errors and mic speech_recognition errors
            self.err_msg()


    def location_getter(self, source):
        while True:
            self.general_display('What country are you looking for? Listening...')
            # Try condition for invalid country and unrecognized speech exceptions
            try:
                listen = self.robot.listen(source)
                # listen to the voice and take the first word if there are many
                place = self.robot.recognize_google(listen).lower().split(' ')
                country = '-'.join(place)
                self.textBrowser_conversation.append(f"\nUser> {place}")
                # If statement validates input country with pycountry module
                if pycountry.countries.search_fuzzy(country):
                    # Url takes america as usa, so this if condition check for that
                    if pycountry.countries.search_fuzzy(country) == pycountry.countries.search_fuzzy("America"):
                        country = "usa"
                    break
                else:
                    # Raise error if country is not validated
                    raise LookupError
            except LookupError or AttributeError:
                # Raised if country not validated
                self.general_display("Invalid Country")
            except speech_recognition.UnknownValueError:
                # Raised if speech not recognized
                self.general_display("Please Say a Country")
        # Get city from the user
        while True:
            self.general_display("What city are you looking for? I'm listening...")
            # Try condition for invalid city and unrecognized speech exceptions
            try:
                listen = self.robot.listen(source)
                # listen to the voice and take the first word if there are many
                place = self.robot.recognize_google(listen).lower().split(' ')
                self.textBrowser_conversation.append(f"\nUser> {place}")
                city = '-'.join(place)
                self.general_display(city + ", " + country)
                break
            except:
                # Raised if speech not recognized
                self.general_display("Please Say a City")

        return country, city

    def general_display(self, msg: str):
        # Since forecast results have successfully been returned say forecast and break loop
        self.textBrowser_conversation.append(f"\nComputer> {msg}\n")
        self.ROBOT_VOICE(msg)
        # print(msg)

    def exit_msg(self):
        # Closing message
        self.general_display('Thank you. Talk to you again soon!')
        self.textBrowser_conversation.append(f"""
        ███████▀█████████████████████████████
        ██████░░█████████████████████████████
        █████▀░▄█████████████████████████████
        █████░░▀▀▀▀▀███▀▀█████▀▀███▀▀▀▀▀█████
        █████░░▄██▄░░███░░███░░███░░███░░████
        ████░░█████░░███░▄███░░██░░▀▀▀░▄█████
        ████░░████▀░███░░███▀░███░░██████████
        ████░░█▀▀░▄████▄░▀▀▀░▄███▄░▀▀▀░▄█████
        █████▄▄▄███████████░░██████▄▄████████
        ██████████████░▀█▀░▄█████████████████
        ███████████████▄▄▄███████████████████
                            """)

    def win_msg(self, num_guess):
        self.general_display('Good job! You guessed my number in ' + str(num_guess) + ' tries.')
        self.textBrowser_conversation.append("""
        █▀▀▄░░░░░░░░░░░▄▀▀█
        ░█░░░▀▄░▄▄▄▄▄░▄▀░░░█
        ░░▀▄░░░▀░░░░░▀░░░▄▀
        ░░░░▌░▄▄░░░▄▄░▐▀▀
        ░░░▐░░█▄░░░▄█░░▌▄▄▀▀▀▀█
        ░░░▌▄▄▀▀░▄░▀▀▄▄▐░░░░░░█
        ▄▀▀▐▀▀░▄▄▄▄▄░▀▀▌▄▄▄░░░█
        █░░░▀▄░█░░░█░▄▀░░░░█▀▀▀
        ░▀▄░░▀░░▀▀▀░░▀░░░▄█▀
        ░░░█░░░░░░░░░░░▄▀▄░▀▄
        ░░░█░░░░░░░░░▄▀█░░█░░█
        ░░░█░░░░░░░░░░░█▄█░░▄▀
        ░░░█░░░░░░░░░░░████▀
        ░░░▀▄▄▀▀▄▄▀▀▄▄▄█▀
                                        """)

    def lose_msg(self, number):
        self.general_display('Sorry, you ran out of attempts. I was thinking of the number ' + number)
        self.textBrowser_conversation.append("""
        ________________________¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶________
        ____________________¶¶¶___________________¶¶¶¶_____
        ________________¶¶¶_________________________¶¶¶¶___
        ______________¶¶______________________________¶¶¶__
        ___________¶¶¶_________________________________¶¶¶_
        _________¶¶_____________________________________¶¶¶
        ________¶¶_________¶¶¶¶¶___________¶¶¶¶¶_________¶¶
        ______¶¶__________¶¶¶¶¶¶__________¶¶¶¶¶¶_________¶¶
        _____¶¶___________¶¶¶¶____________¶¶¶¶___________¶¶
        ____¶¶___________________________________________¶¶
        ___¶¶___________________________________________¶¶_
        __¶¶____________________¶¶¶¶____________________¶¶_
        _¶¶_______________¶¶¶¶¶¶¶¶¶¶¶¶¶¶¶______________¶¶__
        _¶¶____________¶¶¶¶___________¶¶¶¶¶___________¶¶___
        ¶¶¶_________¶¶¶__________________¶¶__________¶¶____
        ¶¶_________¶______________________¶¶________¶¶_____
        ¶¶¶______¶________________________¶¶_______¶¶______
        ¶¶¶_____¶_________________________¶¶_____¶¶________
        _¶¶¶___________________________________¶¶__________
        __¶¶¶________________________________¶¶____________
        ___¶¶¶____________________________¶¶_______________
        ____¶¶¶¶______________________¶¶¶__________________
        _______¶¶¶¶¶_____________¶¶¶¶¶_____________________
                                """)

    def err_msg(self):
        self.general_display("Err! Check your microphone!")
        self.textBrowser_conversation.append("""
        ░░░░░░░░░░░░▄▄▄█▀▀▀▀▀▀▀▀█▄▄▄░░░░░░░░░░░░
        ░░░░░░░░▄▄█▀▀░░░░░░░░░░░░░░▀▀█▄▄░░░░░░░░
        ░░░░░░▄█▀░░░░▄▄▄▄▄▄▄░░░░░░░░░░░▀█▄░░░░░░
        ░░░░▄█▀░░░▄██▄▄▄▄▄▄▄██▄░░░░▄█▀▀▀▀██▄░░░░
        ░░░█▀░░░░█▀▀▀░░▄██░░▄▄█░░░██▀▀▀███▄██░░░
        ░░█░░░░░░▀█▀▀▀▀▀▀▀▀▀██▀░░░▀█▀▀▀▀███▄▄█░░
        ░█░░░░░░░░░▀▀█▄▄██▀▀░░░░░░░░▀▄▄▄░░░▄▄▀█░
        █▀░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▀▀▀▀▀░░▀█
        █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄░░░░█
        █░░░░░░░░░░░░░░░░░░░░░░░░▄▄▄▄▄██░░▀█░░░█
        █░░░░░░░░░░░░░░█░░░▄▄▄█▀▀▀░░░▄█▀░░░░░░░█
        █░░░░░░░░░░░░░░░░░░▀░░░░░░░░█▀░░░░░░░░░█
        █▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄█
        ░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█░
        ░░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█░░
        ░░░█▄░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄█░░░
        ░░░░▀█▄░░░░░░░░░░░░░░░░░░░░░░░░░░▄█▀░░░░
        ░░░░░░▀█▄░░░░░░░░░░░░░░░░░░░░░░▄█▀░░░░░░
                    ★─▄█▀▀║░▄█▀▄║▄█▀▄║██▀▄║─★
                    ★─██║▀█║██║█║██║█║██║█║─★
                    ★─▀███▀║▀██▀║▀██▀║███▀║─★
                    ★───────────────────────★
                    ★───▐█▀▄─ ▀▄─▄▀ █▀▀──█───★
                    ★───▐█▀▀▄ ──█── █▀▀──▀───★
                    ★───▐█▄▄▀ ──▀── ▀▀▀──▄───★
                    """)


if __name__ == "__main__":
    app = QApplication([])
    window = SpeechWebScraper()
    window.show()
    sys.exit(app.exec_())

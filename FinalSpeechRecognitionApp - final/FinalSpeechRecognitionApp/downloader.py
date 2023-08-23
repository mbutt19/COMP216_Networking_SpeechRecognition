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
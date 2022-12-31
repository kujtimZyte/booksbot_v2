import re

...

def parse(self, response):
    for term in response.css("div.col-md-8"):
        description = term.css("main.mb-3::text").get()
        description = re.sub(r"[A-Za-z]+ teriminin tıbbi anlamı;", "", description)
        yield {
            "name": term.css("h1.display-5::text").get(),
            "description": description,
        }

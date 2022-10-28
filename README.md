# Gas and routes calculation app

GASCALC is an app, developed to be used by company accountant.

## Description

The goal is to calculate cost of planned work-day travels of company employee and to provide formal report to accountant.

Calculation of cost depends on several factors:

1. Employee's typical destination points
2. Employee's car (gas consumption)
3. Number of travels per day

## Typical usage case

1. Authorization
2. Creation of new employee, car, destination point or importing via Excel/csv file
	- Destination points created by filling address form, then geocoding address in coordinates
3. Calculation
	- Choice of employee, car, day destination points
	- Calculation of random route variants (A-B-C-D-A, A-C-B-A, A-D-C-B_A, etc.)
	- Calculation of routes proveded via openrouteservice API
4. Export of calculaions in form of Word or pdf report, consisting necessary legal information

## Tech stack used

###### Application

- Flask
- HTML, CSS, Bootstrap

###### External services for map, markers, routing and geocoding

- Openrouteservice 
- Geopy
- Folium

## TO-DO

- gas prices data parsing
- change of routing service, to take into account traffic jams data

## Author commentary

This is the production version of the app, uploaded in public repository for demonstrative purposes.
“TO-DO” section unneeded to demonstrate code and project, but I chose to include it deliberately, because some code refers to these unimplemented features. App is in use now, but those features aren't needed anymore. Finishing them is unnecessary extra work, and I don’t want to break the code, in order for you to see even my drafts, not just the finished product.

I am very critical to my code quality in this app, but lack of time doesn’t help me to build it into a better portfolio example. My thoughts on problems with this app (as-is) :

1. Wrong back-end framework. Now, with more experience, I think of Django being better for this app development. Mainly because Flask blueprints are basically what Django provides right from the box with a project applications system. Django-powered project would be cleaner and more structured.

2. Again, if Django was my first choice, I would use class-based views concept, to organize views and templates properly. Flask projects structure predisposes to use functional programming, while this app complexity demands a more object-oriented approach.

3. Lack of API's communication proper handling. While there is basic exception handling provided, any API communication change would bring unhandled errors.

While it is maybe not a good tactic to provide my future employer with problematic code hints, my choice is deliberate. I want you to know, that

- I clearly see problems in my code and in its structure
- I don’t afraid to say that I did something wrong
- I have clear vision on how to improve my code

Thank you for your time! I hope this commentary is useful.
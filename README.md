# TRMNL service for Apple Notes using Flask

This repo contains:
* A Flask-based server.py file containing two endpoints for use with the [TRMNL](https://usetrmnl.com) e-ink display.
  * These endpoints connect with the TRMNL's webhooks for private plugins for two features.
    * /freezer-list - A list of items in your freezer
    * /meal-plan - A weekly dinner meal planner
  * Data handled by this API is sent from two Apple Shortcuts (one for each feature) that grab contents of an Apple Note and send it to the server. In my use case, this Flask server is running on a raspberrypi.
* A .service file to handle running the Flask server on the raspberrypi using systemctl.
* A deploy script that will copy over the server.py and note-api.service files onto the raspberrypi, for easy development.
* Backups of the HTML files used in TRMNL's markup to display the data.

You'll need to create a config.py file containing the webhook urls.
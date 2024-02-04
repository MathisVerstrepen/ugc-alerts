![ReadMe Banner](https://github.com/MathisVerstrepen/github-visual-assets/blob/main/banner/UGC-Alerts.png?raw=true)

# UGC New Movies Screenings Alert

This script is a simple web scraper that checks the UGC website for new movie screenings. If it finds any, it sends an discord alert to a specified channel.

![Splitter-1](https://raw.githubusercontent.com/MathisVerstrepen/github-visual-assets/main/splitter/splitter-1.png)

## Features

- UGC website web scraping
- Discord webhook integration

![Splitter-1](https://raw.githubusercontent.com/MathisVerstrepen/github-visual-assets/main/splitter/splitter-1.png)

## How it works

The script uses the `requests` and `beautifulsoup4` libraries to scrape the UGC website. It checks the website for new movie screenings and sends a discord alert if it finds any. 

The script is run as a docker container and is deployed as a cronjob every 10 minutes.

![Splitter-1](https://raw.githubusercontent.com/MathisVerstrepen/github-visual-assets/main/splitter/splitter-1.png)


## Deployment

This script is not meant to be run on another system than mine. It is not very user friendly and I have no intention of making it so. If you want to use it, you will have to modify it to suit your needs. 

Currently, the script is deployed as a docker container and run as a cronjob every 10 minutes. The docker container is built automatically using my custom deployment pipeline that can be found [not yet public].
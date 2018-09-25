# TripAdvisor

This project is a simple Python program which is designed to scrape information on [TripAdvisor](https://www.tripadvisor.com/) website.

Current features:

* **Overall** information: which returns the following data for each city:
   * number of vactional rentals
   * number of vacational rentals' reviews
   * number of restaurants
   * number of restaurants' reviews
   * number of hotels
   * number of hotels' reviews
   * number of things to do
   * number of things to do reviews
   * number of forum's question
   * number of flight
* **Restaurant** information: This feature extracts the following data for each review in restaurant:
   * Username
   * Date
   * Title
   * Review Text
   * Rate

## How do I use this?

For installation follow the instructions below:

* [Requirements](#):

  * Python3

  * Redis Server: Redis has been used to cache the data for avoiding downloading them again and again.

    ```bash
    sudo apt install redis-server python3 python3-pip
    ```

## Want to develop on TripAdvisor?

This gets you started:

```bash
$ git clone https://github.com/GreatBahram/TripAdvisor.git
$ cd TripAdvisor
$ virtualenv venv
$ . venv/bin/activate
$ pip3 install -r requirements.txt 
$ python3 run.py -h
$ python3 run.py overall lima tokyo riyadh vienna shanghai taipei
$ python3 run.py restaurant london paris melbourne
```

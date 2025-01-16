#!./.venv/bin/python 

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
driver = webdriver.Chrome()

html_base = ' \
<!DOCTYPE html> \
<html lang="en"> \
<head> \
    <meta charset="UTF-8"> \
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> \
    <title>Layout Example</title> \
    <style> \
        body { \
            font-family: Arial, sans-serif; \
        } \
        .container { \
            margin: 20px; \
        } \
        .layout { \
            margin-bottom: 40px; \
        } \
        .image-with-text { \
            display: flex; \
            align-items: center; \
            margin-bottom: 20px; \
        } \
        .image-with-text img { \
            width: 250px; \
            height: 350px; \
            margin-right: 10px; \
        } \
        .grid { \
            display: grid; \
            grid-template-columns: repeat(4, 1fr); \
            grid-gap: 10px; \
        } \
        .grid img { \
            width: 250px; \
            height: 350px; \
        } \
        .grid-item { \
            display: flex; \
            align-items: center; \
        } \
        .grid-item .text { \
            margin-left: 10px; \
        } \
    </style> \
</head> \
<body> \
 \
<div class="container"> \
    CONTAINER_BODY \
</div> \
 \
</body> \
</html> \
'

def generate_card_url(card):
    card_url = 'https://onepiecetopdecks.com/wp-content/gallery/SET/CARD.jpg'
    setid = card.split('-')[0].lower()
    if setid == 'p':
        setid == 'p01'
    return card_url.replace('SET', setid, 1).replace('CARD', card, 1)

def generate_deck_base(leader, count):
    deck_base = ' \
        <div class="layout"> \
            <div class="image-with-text"> \
                <img src="LEADER_IMAGE" alt="A leader image."> \
                <span>Count: LEADER_COUNT</span> \
            </div> \
            <div class="grid"> \
                    CARD_INSTANCES \
            </div> \
        </div> \
    '
    leader_url = generate_card_url(leader)
    return deck_base.replace('LEADER_IMAGE', leader_url, 1).replace('LEADER_COUNT', str(count), 1)

def generate_card_instance(card, percent, avg):
    card_base=' \
                <div class="grid-item"> \
                    <img src="CARD_IMAGE" alt="Grid 1"> \
                    <div class="text"> \
                        <span>Percent: PERCENT%</span><br> \
                        <span>Avg: AVG</span> \
                    </div> \
                </div> \
    '
    card_url = generate_card_url(card)
    return card_base.replace('CARD_IMAGE', card_url, 1).replace('PERCENT', '{:.2f}'.format(percent), 1).replace('AVG', str(avg), 1)


try:
    # Load the page with Selenium
    url = "https://onepiecetopdecks.com/deck-list/english-op-09-the-new-emperor-decks/"
    driver.get(url)

    # Optionally wait for the content to load
    driver.implicitly_wait(10)  # Adjust the timeout as needed

    # Get the page source and pass it to BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Use BeautifulSoup to locate the <tbody> with the specified class
    tbody = soup.find("tbody", class_="row-striping row-hover")

    # deck
    # index by leader id
    #   total count
    #   cardid
    #       list of counts across decks

    decks = {}

    if tbody:
        # Iterate through the rows (<tr> tags) inside the <tbody>
        for row in tbody.find_all("tr"):
            # Extract data from each row
            columns = [col.get_text(strip=True) for col in row.find_all("td")]
            deckstring = columns[0]
            # print(f'Deckstring: {deckstring}')
            cardlist = [card.split('n') for card in deckstring.split('a')]

            leader = cardlist[0][1]
            decklist_body = cardlist[1:]

            if not leader in decks:
                decks[leader] = {}
                decks[leader]["count"] = 0

            targetdeck = decks[leader]
            targetdeck["count"] = targetdeck["count"] + 1

            for card_count in decklist_body:
                cardid = card_count[1]
                if not cardid in targetdeck:
                    targetdeck[cardid] = []

                targetdeck[cardid] += [int(card_count[0])]
    else:
        print("No <tbody> with the specified class found.")

    decks_html = ''

    # generate sorted list of leaders

    leaders_sorted = [leader for leader in decks]
    leaders_sorted = sorted(leaders_sorted, key=lambda leader: -decks[leader]['count'])

    for leader in leaders_sorted:
        body = decks[leader]

        # print(f'Deck Leader: {leader}')
        # print(f'\tCount: {body["count"]}')

        deck_base = generate_deck_base(leader, body["count"])

        grid = ''

        cards_sorted = [card for card in body]
        cards_sorted.remove('count')
        cards_sorted = sorted(cards_sorted, key=lambda card: -len(body[card]))

        for cardid in cards_sorted:
            counts = body[cardid]

            # print(f'\tCard: {cardid}')
            count =  len(counts)
            percent = (len(counts) / body['count']) * 100
            avg = sum(counts) / len(counts)
            # print(f'\t\tCount: {count}')
            # print(f'\t\tPercent: {percent}')
            # print(f'\t\tAvg: {avg}')

            grid += '\n'
            grid += generate_card_instance(cardid, percent, avg)

        finalized_deck_base = deck_base.replace('CARD_INSTANCES', grid, 1)
        decks_html += '\n'
        decks_html += finalized_deck_base

    final_html = html_base.replace('CONTAINER_BODY', decks_html, 1)

    out = open('out.html', 'w')
    out.write(final_html)
    out.close()

finally:
    # Close the Selenium WebDriver
    driver.quit()

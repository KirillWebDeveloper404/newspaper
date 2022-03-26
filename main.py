import time

import requests
from bs4 import BeautifulSoup
import telebot

bot = telebot.TeleBot('2057155172:AAGzNarSXOFWHkpU7Ul_RcCPJXmygtLBkQk')

def EscapeHTML(text):
    return str(text).replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

def parsing_card_nftcalendar(url):
    try:
        r = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'})

        print('[PARSER] Got the page')
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html5lib')
            name = soup.find('h1').get_text()

            print('[PARSER] Name: %s' % name)
            print(f'[PARSER] New Post url: {url}')
            photo = soup.find('figure', class_='image').find('img')['src']

            desc = ''
            for elem in soup.find('div', class_='column is-three-quarters').find_all('p'):
                try:
                    try:
                        if 'is-size-6' in elem['class']:
                            break
                        else:
                            desc += elem.get_text() + '\n'
                    except:
                        desc += elem.get_text() + '\n'
                except:
                    print(elem)

            desc = desc.strip()

            if len(desc) == 0:
                desc = 'No description'


            # getting links
            links = []
            cards = soup.find('footer', class_='card-footer').find_all('a')
            for card in cards:
                nameOfLink = None
                iconElem = card.find('span', class_='icon').find('i')
                if 'fa-window-maximize' in iconElem['class']:
                    nameOfLink = 'Website'
                elif 'fa-discord' in iconElem['class']:
                    nameOfLink = 'Discord'
                elif 'fa-twitter' in iconElem['class']:
                    nameOfLink = 'Twitter'
                else:
                    continue
                try:
                    if 'http' in card['href']: links.append((nameOfLink, card['href']))
                except:
                    pass

            # getting date
            dates = soup.find_all('div', class_='box is-shadowless has-background-white-bis is-radiusless mb-2')
            date = ''
            for el in dates:
                texts = el.get_text().splitlines()
                text = ''
                for tel in texts:
                    text += tel.replace('\t', '')

                if 'Presale' in text or 'Public Drop' in text:
                    print(text)
                    date += text

            print('[PARSER] Sending to Telegram...')
            key = telebot.types.InlineKeyboardMarkup()
            for i in range(len(links)):
                key.add(telebot.types.InlineKeyboardButton(text=links[i][0], url=links[i][1]))

            try:
                bot.send_photo(-1001546146131, requests.get(photo).content, caption=f'<b>{name}\n{date}</b>\n<i>{desc}</i>',
                                   parse_mode='HTML', reply_markup=key)
            except:
                try:
                    time.sleep(0.3)
                    bot.send_photo(-1001546146131, requests.get(photo).content)
                    time.sleep(0.3)
                    bot.send_message(-1001546146131, f'<b>{EscapeHTML(name)}</b>\n<i>{EscapeHTML(desc)}</i>',
                                   parse_mode='HTML', reply_markup=key)
                except Exception as e:
                    print(e)
                    try:
                        time.sleep(0.3)
                        bot.send_message(-1001546146131, f'<b>{EscapeHTML(name)}</b>\n<i>{EscapeHTML(desc)}</i>',
                                             parse_mode='HTML', reply_markup=key)
                    except:
                        try:
                            time.sleep(0.3)
                            bot.send_message(-1001546146131, f'<b>{EscapeHTML(name)}</b>',
                                                 parse_mode='HTML', reply_markup=key)
                        except:
                            time.sleep(5)
            print('[PARSER] Telegram Send Success')
            sleepTime = 60 * 5
            print('[PARSER] Sleeping for %s seconds' % sleepTime)
            time.sleep(sleepTime)
    except Exception as e:
        print(str(e))
        print(f'[PARSER] Error: {str(e)}, Sleep!')
        time.sleep(60)

def IsInCache(url):
    return url in open('cachecheck.txt', 'r', encoding='utf-8').read().split('\n')

def AddToCache(url):
    with open('cachecheck.txt', 'a', encoding='utf-8') as f:
        f.write(f'{url}\n')



def main():
    while True:
        print('[NFT] Start Checking')
        try:
            r = requests.get('https://nextdrop.is/upcoming-nft-drops', headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'referer': 'https://www.google.com/'})

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html5lib')

                table = soup.find('table', class_='table is-size-6 is-fullwidth is-hoverable')
                elems = table.find_all('tbody')
                links = []
                for t in elems:
                    links.append(t.find_all('td')[2].a['href'])

                print(f'[NFT] Links count: {len(links)}')
                for link in links:
                    if IsInCache(link): continue

                    print('[NFT] Parsing %s' % link)
                    parsing_card_nftcalendar('https://nextdrop.is' + link)
                    print('[NFT] Parsed %s' % link)

                    AddToCache(link)
            print('[NFT] Sleep')
            time.sleep(120)
        except Exception as e:
            print(f'[NFT] Error: {str(e)}, Sleep!')
            time.sleep(60)



if __name__=="__main__":
    main()



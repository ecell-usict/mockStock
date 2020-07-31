# Note to future reader/editor of this code:-
# --> The round1[email]['buy'] key serves as a buffer/holder for all shares owned throughout all 3 rounds.
# --> If you want only round1 results, comment all the code that comes after it and view the results.
# --> This code was made in a very short time to cater to mockstock needs, hence isnt very modular, and highly spaghetti.
# --> Needs cleaning but works well.
#--> Future editor, can take round divisions and make them Functions.

from csv import DictReader
from round1 import round1
from round2 import round2
from round3 import round3

listings = {}
compList = []
emails = list(round1.keys())
emails2 = list(round2.keys())
emails3 = list(round3.keys())

with open("listings.csv") as file:
    listing_seq = DictReader(file)
    for company in listing_seq:
        compList.append(company['companies'].lower())
        listings.update({
            f"{company['companies'].lower()}": {
                "p1": company["p1"],
                "p2": company["p2"],
                "p3": company["p3"],
                "p4": company["p4"]
            }
        })
        #print(company['companies'].lower()) TEST




############################# ROUND 1 RESULTS  ###################################################################     
#loop over a list of emails and insert this inside of this master loop:-
for email in emails:
    if email in round1.keys():
        short = 0
        margin = 0
        round1[email]['cash'] += round1[email]['loan']
        for stock in compList:
            #implementing normal buy transaction
            if stock in round1[email]["buy"].keys():
                subtract_this = int(listings[stock]['p1'])*round1[email]["buy"][stock]
                round1[email]['cash'] = round1[email]['cash'] - subtract_this

            #implementing sell transaction (Which will come from round 2 onwards)

            #implementing short sell transaction:-
            if stock in round1[email]["short"].keys():
                add_this = (int(listings[stock]['p1']) - int(listings[stock]['p2'])) * round1[email]["short"][stock]
                short = short + add_this

            #implementing margin trading transaction:-
            if stock in round1[email]["margin"].keys():
                add_margin = (int(listings[stock]['p2']) - int(listings[stock]['p1'])) * round1[email]["margin"][stock]
                margin = margin + add_margin

        #short sell 50k rule:-
        if (short > 50000):
            short = 0
        round1[email]['cash'] = round1[email]['cash'] + short

        #margin trade rules
        if margin > (4*round1[email]["cash"]):
            margin = 0
        round1[email]['cash'] = round1[email]['cash'] + margin

    else:
        continue
############################# END ROUND 1 RESULTS ################################################################


############################# TESTING FOR ROUND 2 RESULTS ########################################################

for email in emails2:
    short = 0
    margin = 0
    was_in_round1 = False
    if email in round1.keys():
        round2[email]['cash'] = round1[email]['cash'] + round2[email]['loan'] - ((round1[email]['loan']*5)/100)
        was_in_round1 = True
    else:
        round2[email]['cash'] = round2[email]['cash'] + round2[email]['loan']

    for stock in compList:
        # implementing buy transaction 
        if stock in round2[email]['buy'].keys():
            subtract = int(listings[stock]['p2'])*round2[email]["buy"][stock]
            round2[email]['cash'] = round2[email]['cash'] - subtract
            if was_in_round1 == True:
                round1[email]['buy'].update({
                    f"{stock}":round2[email]['buy'][stock]   # ADDING OWNED STOCKS TO THE ROUND 1 BUFFER
                })


        #implementing sell transaction
        if stock in round2[email]['sell']:
            if was_in_round1 == True:
                if stock in round1[email]['buy']:
                    if round2[email]['sell'][stock] <= round1[email]['buy'][stock]:
                        round1[email]['buy'][stock] = round1[email]['buy'][stock] - round2[email]['sell'][stock] #Round1 buffer edit

                        add = int(listings[stock]['p2'])*round2[email]["sell"][stock]
                        round2[email]['cash'] = round2[email]['cash'] + add

        # Implementing short sell transaction:-
            if stock in round2[email]["short"].keys():
                add_to_short = (int(listings[stock]['p2']) - int(listings[stock]['p3'])) * round2[email]["short"][stock]
                short = short + add_to_short

        # Implementing margin trading transaction:-
            if stock in round2[email]["margin"].keys():
                add_to_margin = (int(listings[stock]['p3']) - int(listings[stock]['p2'])) * round2[email]["margin"][stock]
                margin = margin + add_to_margin

    #short sell 50k rule:-
    if (short > 50000):
        short = 0
    round2[email]['cash'] = round2[email]['cash'] + short

    #margin trade rules
    if margin > (4*round2[email]["cash"]):
        margin = 0
    round2[email]['cash'] = round2[email]['cash'] + margin
    
                



############################# END TESTING FOR ROUND 2 RESULTS ####################################################

############################# TESTING FOR ROUND 3 RESULTS ########################################################

for email in emails3:
    was_in_1 = False
    was_in_2 = False
    if email in emails2:
        was_in_2 = True
    if email in emails:
        was_in_1 = True

    if was_in_1 == True:
        if was_in_2 == True:
            round3[email]['cash'] = round2[email]['cash'] - ((round1[email]['loan']*5)/100) - ((round2[email]['loan']*5)/100) + round3[email]['loan']

        else:
            round3[email]['cash'] = round1[email]['cash'] - ((round1[email]['loan']*5)/100) + round3[email]['loan']

    elif was_in_2 == True:
        round3[email]['cash'] = round2[email]['cash'] - ((round2[email]['loan']*5)/100) + round3[email]['loan']

    else:
        round3[email]['cash'] = 100000


    for stock in compList:
        # Implementing buy transaction:-
        if stock in round3[email]['buy'].keys():
            subtract_amt = int(listings[stock]['p3'])*round3[email]["buy"][stock]
            round3[email]['cash'] = round3[email]['cash'] - subtract_amt
            if was_in_1 == True:
                if was_in_2 == True:
                    round1[email]['buy'].update({
                        f"{stock}":round3[email]['buy'][stock]   # ADDING OWNED STOCKS TO THE ROUND 1 BUFFER
                    })

            elif was_in_2 == True:
                round2[email]['buy'].update({
                    f"{stock}":round3[email]['buy'][stock]   # ADDING OWNED STOCKS TO THE ROUND 2 BUFFER
                })

            else:
                pass

        # Implementing Sell transaction:-
        if stock in round3[email]['sell']:
            if was_in_1 == True:
                if stock in round1[email]['buy']:
                    if round3[email]['sell'][stock] <= round1[email]['buy'][stock]:
                        round1[email]['buy'][stock] = round1[email]['buy'][stock] - round3[email]['sell'][stock] #Round1 buffer edit

                        add = int(listings[stock]['p3'])*round3[email]["sell"][stock]
                        round3[email]['cash'] = round3[email]['cash'] + add

            elif was_in_2 == True:
                if stock in round2[email]['buy']:
                    if round3[email]['sell'][stock] <= round2[email]['buy'][stock]:
                        round2[email]['buy'][stock] = round2[email]['buy'][stock] - round3[email]['sell'][stock] #Round1 buffer edit

                        add = int(listings[stock]['p3'])*round3[email]["sell"][stock]
                        round3[email]['cash'] = round3[email]['cash'] + add  

            else:
                pass

        # Implementing short sell:-
            if stock in round3[email]["short"].keys():
                add_to_short = (int(listings[stock]['p3']) - int(listings[stock]['p4'])) * round3[email]["short"][stock]
                short = short + add_to_short        


        # Implementing margin trading:-
            if stock in round3[email]["margin"].keys():
                add_to_margin = (int(listings[stock]['p4']) - int(listings[stock]['p3'])) * round3[email]["margin"][stock]
                margin = margin + add_to_margin     

    #short sell 50k rule:-
    if (short > 50000):
        short = 0
    round3[email]['cash'] = round3[email]['cash'] + short

    #margin trade rules
    if margin > (4*round3[email]["cash"]):
        margin = 0
    round3[email]['cash'] = round3[email]['cash'] + margin
        
        

#make final code to calculate net worth
for email in emails3:
    print(f"{email} - {round3[email]['cash']}")

print("__________________________________________________________________________________")



############################# END TESTING FOR ROUND 3 RESULTS ########################################################

for email in emails3:
    if email in emails:
        if email in emails2:
            round3[email]['cash'] = round3[email]['cash'] - round1[email]['loan'] - round2[email]['loan'] - round3[email]['loan'] - ((round3[email]['loan']*5)/100)
            for stockey in round1[email]["buy"].keys():
                round3[email]['cash'] += (round1[email]['buy'][stockey]*int(listings[stockey]['p4']))

    elif email in emails2:
        round3[email]['cash'] = round3[email]['cash'] - round2[email]['loan'] - round3[email]['loan'] - ((round3[email]['loan']*5)/100)
        for stockey in round2[email]['buy']:
            round3[email]['cash'] += (round2[email]['buy'][stockey]*int(listings[stockey]['p4']))

    else:
        round3[email]['cash'] = round3[email]['cash'] - round3[email]['loan'] - ((round3[email]['loan']*5)/100)
        for stockey in round3[email]['buy']: 
            round3[email]['cash'] += (round3[email]['buy'][stockey]*int(listings[stockey]['p4']))

    print(f"{email} - {round3[email]['cash']}") # final net worth


print("______________________________________________________")

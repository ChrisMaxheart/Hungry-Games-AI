#
# CS1010S --- Programming Methodology
#
# Contest 15.1 Template
#
# Note that written answers are commented out to allow us to run your
# code easily while grading your problem set.

from hungry_games_classes import *
from contest_simulation import *
import random

#udahlah submit ini aja

class SHK(Tribute):
    #so generally, my AI will think all possible move, where each function will decide each best move for each commands (I will determine via scoring what is the best move for each situation). And lastly, the next_action function which commands is the best for current situation
    #I will make this quite complicated to prepare for the contest lol
    def next_action(self):
        
        
        #helper function
        def meddmg(weapon): #median damage of the weapon
            return 0.5 * (weapon.max_damage() + weapon.min_damage())

        def weapow(weapon): #weapon power, use median damage and shots left factor
            if isinstance(weapon, Weapon):    
                if isinstance(weapon, RangedWeapon):
                    if weapon.shots_left() == 0:
                        return 0
                    else:
                        return meddmg(weapon)
                else:
                    return meddmg(weapon)
            else:
                return 0

        def strongestweapon(weaplist): #strongest weapon
            lst = list(map(lambda x: [x, weapow(x)], weaplist))
            if lst != []:
                lst.sort(key = lambda x: x[1], reverse = True)
                return lst[0][0]
            else:
                return 0

        def strongestmelee(weaplist): #strongest melee weapon
            lst = list(map(lambda x: [x, weapow(x)], filter(lambda x: (not isinstance(x, RangedWeapon)), weaplist)))
            if lst != []:
                lst.sort(key = lambda x: x[1], reverse = True)
                return lst[0][0]
            else:
                return 0

        #this is just all the information that I might or might not need

        myhp = self.get_health() #return int
        myweap = list(self.get_weapons()) #return list
        myfood = list(filter(lambda x: x.get_food_value() > 0, self.get_food())) #return list
        mymed = list(filter(lambda x: x.get_medicine_value() > 0, self.get_medicine())) #return list
        cond = self.objects_around() #return list
        exits = self.get_exits() #return list
        myhung = self.get_hunger() #return int
        myinven = self.get_inventory() #return list
        myammo = list(map(lambda x: [x, x.weapon_type(), x.get_quantity()], filter(lambda x: isinstance(x, Ammo), myinven))) #return list, contain my ammo list, weapon it suited for, and quantity
        enemytribute = list(map(lambda x: [x, x.get_health(), weapow(strongestweapon(x.get_weapons()))], filter(lambda x: isinstance(x, Tribute), cond))) #i want to see what enemy is there, which its hp and strongest weapon displayed
        enemywildanimals = list(map(lambda x: [x, x.get_health(), x.get_damage()], filter(lambda x: isinstance(x, WildAnimal), cond)))
        enemy = enemytribute + enemywildanimals
        animals = list(map(lambda x: [x, x.get_health(), x.get_food_value()], filter(lambda x: isinstance(x, Animal), cond))) #list of all animals available with animal health and food value
        foodlst = list(map(lambda x: [x, x.get_food_value()], filter(lambda x: isinstance(x, Food), cond))) #list of all foods
        medlst = list(map(lambda x: [x, x.get_medicine_value(), x.get_food_value()], filter(lambda x: isinstance(x, Medicine), cond))) #list of all medicine
        ammlst = list(map(lambda x: [x, x.weapon_type(), x.get_quantity()], filter(lambda x: isinstance(x, Ammo), cond))) #list of all ammo
        weaplst = list(filter(lambda x: isinstance(x, Weapon), cond)) #list of all weapon in cond

        #assuming this move is the best, think about the targets function

        def thinkfight(myweap, enemy):  #best attacking move to other tribute
            targets = enemy
            strongest = strongestweapon(myweap)
            targets.sort(key = lambda x: x[1]) #sort based on difference of number of turns to kill each other
            target = targets[0]
            return (target[0], strongest)

        def thinkhunt(myweap, animals): #best attacking move to animals
            targets = animals
            strongest = strongestmelee(myweap)
            if type(strongest) == int:
                strongest = strongestweapon(myweap)
            targets.sort(key = lambda x: x[2], reverse = True)
            targets.sort(key = lambda x: x[1]//(weapow(strongest)+0.1)) #sort based on how many turns I can kill it, if tie, food value wins
            target = targets[0]
            return (target[0], strongest)

        def thinktakefood(lst): #best taking food move
            foods = lst
            foods.sort(key = lambda x: x[1], reverse = True) #based on food value
            return foods[0][0]

        def thinktakemed(lst): #best taking medicine move
            meds = lst
            meds.sort(key = lambda x: x[2], reverse = True) #based on med val, if tie, food value wins
            meds.sort(key = lambda x: x[1], reverse = True)
            return meds[0][0]

        def thinktakeweap(lst): #best taking weapon move
            strongest = strongestweapon(lst)
            melee = strongestmelee(lst)
            if type(melee) == int:
                return strongest
            elif strongest == melee:
                return strongest
            else:
                if (shots_left(strongest) == 0) or ((weapow(strongest)-weapow(melee)) <= 5) :
                    return melee
                else:
                    return strongest #look for the strongest weapon, have a bit preference with melee

        def thinktakeammo(lst): #best taking ammo move
            amm = lst
            amm.sort(key = lambda x: x[2], reverse = True)
            myweapname = list(map(lambda x: x.get_name(), myweap))
            newamm = list(filter(lambda x: x[1] in myweapname, amm))
            if newamm == []:
                return amm[0][0]
            else:
                return newamm[0][0] #look for ammo that I have the weapon, if tie, highest quantity wins

        def thinkeatfood(lst): #best eating food (non med) move
            foodlst = lst
            foodlst.sort(key = lambda x: abs(x.get_food_value()-(myhung))) #try to be efficient, just take food which is as close as possible with my hunger loss
            newlist = list(filter(lambda x: x not in mymed, foodlst))
            if newlist == []:
                return foodlst[0]
            else:
                return newlist[0]

        def thinkeatmed(lst): #best eating medicine move
            medlst = lst
            medlst.sort(key = lambda x: abs(x.get_food_value()-(myhung)))
            medlst.sort(key = lambda x: abs(x.get_medicine_value()-(100-myhp))) #try to be efficient for hp gain, if tie, efficient for hunger gain
            return medlst[0]

        def thinkload(weap, ammo): #best load move
            nameweap = list(map(lambda x: x.get_name(), weap))
            amm = ammo
            amm.sort(key = lambda x: x[2], reverse = True)
            newamm = list(filter(lambda x: x[1] in nameweap, amm)) #same logic as taking ammo
            if newamm != []:
                idx = nameweap.index(newamm[0][1])
                return (weap[idx], newamm[0][0])
            else:
                return 0

        #this is the scoring part
        consideration = [0,11,13,14,15,12,0,0,10,0,0] #attack0, hunt1, takefood2, takemed3, takeweapon4, takeammo5, eatfood6, eatmed7, go8, load9, and None10, respectively (the number is the index of the list)

        if type(strongestweapon(myweap)) == int:
            power = 0
        else:
            power = weapow(strongestweapon(myweap))

        #this is to prevent the impossible part, and to try to fulfil basic needs
        if type(thinkload(myweap, myammo)) == int: #cannot load
            consideration[9] = -100000
        if enemy == []:
            consideration[0] = -100000
        if animals == []: 
            consideration[1] = -100000
        if myfood == []:
            consideration[6] = -100000
            consideration[1] += 999
            consideration[2] += 2000
        if power == 0:
            consideration[0] = -100000
            consideration[1] = -100000
            consideration[4] += 1500
        if mymed == []:
            consideration[7] = -100000
            consideration[3] += 2000
        if foodlst == []:
            consideration[2] = -100000
        if medlst == []:
            consideration[3] = -100000
        if weaplst == []:
            consideration[4] = -100000
        if ammlst == []:
            consideration[5] = -100000

        #this part is for the logic scoring
        
        if power == 0:
            consideration[0] = -100000
            consideration[1] = -100000
            consideration[4] += 1500
            consideration[5] += 500
        if enemy != []: #if I can kill everyone without getting me killed, just kill them
            enemydmg = list(map(lambda x: x[2], enemy))
            totaldmg = 0
            enemyhealth = list(map(lambda x: x[1], enemy))
            totalhealth = 0
            for i in range(len(enemydmg)):
                totaldmg += enemydmg[i]
                totalhealth += enemyhealth[i]
            if totaldmg >= myhp:
                consideration[8] += 100000
            elif totaldmg == 0:
                consideration[0] += 10000
            elif myhp//totaldmg > totalhealth//power:
                consideration[0] += 10000
            elif power == 0:
                consideration[8] += 1000
            else:
                consideration[8] += 1000
            newenemy = enemy
            newenemy.sort(key = lambda x: x[1])
            if newenemy[0][1] < power:
                consideration[0] += 10000
            
        if animals != []:
            newanimals = animals
            newanimals.sort(key = lambda x: x[1])
            if newanimals[0][1] < power:
                consideration[1] += 9990
        if myhp < 50: #this is if my hp is low try to find medicine
            if mymed == []:
                consideration[3] += 9999
                if medlst == []:
                    consideration[8] += 1000
            else:
                consideration[7] += 9999
        elif myhp <75:
            if mymed == []:
                consideration[3] += 450
                if medlst == []:
                    consideration[8] += 50
            else:
                consideration[7] += 450            
        if myhung > 50: #if my hunger is high try to find food
            if myfood == []:
                consideration[2] += 9898
                consideration[1] += 200
                if foodlst == []:
                    consideration[8] += 100
            else:
                consideration[6] += 9898
        elif myhung > 25:
            if myfood == []:
                consideration[2] += 440
                consideration[1] += 50
                if foodlst == []:
                    consideration[8] += 20
            else:
                consideration[6] += 440
        if cond == []:
            consideration[8] += 1000

        #this is the command part
        maxi = consideration.index(max(consideration)) #finding max score
        if maxi == 0:
            myact = thinkfight(myweap, enemy)
            return ("ATTACK", myact[0], myact[1])
        elif maxi == 1:
            myact = thinkhunt(myweap, animals)
            return ("ATTACK", myact[0], myact[1])
        elif maxi == 2:
            return ("TAKE", thinktakefood(foodlst))
        elif maxi == 3:
            return ("TAKE", thinktakemed(medlst))
        elif maxi == 4:
            return ("TAKE", thinktakeweap(weaplst))
        elif maxi == 5:
            return ("TAKE", thinktakeammo(ammlst))
        elif maxi == 6:
            return ("EAT", thinkeatfood(myfood))
        elif maxi == 7:
            return ("EAT", thinkeatmed(mymed))
        elif maxi == 8:
            index = random.randint(0, len(exits)-1)
            direction = exits[index]
            return ("GO", direction)
        elif maxi == 9:
            myact = thinkload(myweap, myammo)
            return ("LOAD", myact[0], myact[1])
        elif maxi == 10:
            return None


#######################################
# Testing Code
#######################################

# We only execute code inside the if statement if this file is
# not being imported into another file
# if __name__ == '__main__':
#     def qualifer_map(size, wrap):
#         game_config = GameConfig()
#         game_config.set_item_count(Weapon, 10)
#         game_config.set_item_count(RangedWeapon, 10)
#         game_config.set_item_count(Food, 10)
#         game_config.set_item_count(Medicine, 10)
#         game_config.set_item_count(Animal, 10)
#         game_config.steps = 1000

#         def spawn_wild_animals(game):
#             for i in range(3):
#                 animal = DefaultItemFactory.create(WildAnimal)
#                 game.add_object(animal[0])
#                 GAME_LOGGER.add_event("SPAWNED", animal[0])
#         game_config.add_periodic_event(20, spawn_wild_animals, "Spawn Wild Animals")

#         return (GameMap(size, wrap=wrap), game_config)

#     # Create 6 AI Clones
#     tributes = []
#     # for i in range(4):
#         # An AI is represented by a tuple, with the Class as the first element,
#         # and the name of the AI as the second
#     ai = (SHK003, "SHK003")
#     tributes.append(ai)

#     # Qualifier Rounds
#     # Uncomments to run more rounds, or modify the rounds list
#     # to include more rounds into the simulation
#     # (Note: More rounds = longer simulation!)
#     rounds = [qualifer_map(4, False),
#               #qualifer_map(4, False),
#               #qualifer_map(4, False),
#               #qualifer_map(4, True),
#               #qualifer_map(4, True),
#               #qualifer_map(4, True),
#              ]



#     match = Match(tributes, rounds)
#     print("Simulating matches... might take a while")

#     # Simulate without the graphics
#     match.text_simulate_all()

#     # Simulate a specific round with the graphics
#     # Due to limitation in the graphics framework,
#     # can only simulate one round at a time
#     # Round id starts from 0
#     # match.gui_simulate_round(0)
